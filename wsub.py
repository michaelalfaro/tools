#!/usr/bin/env python

"""wsub.py: Vital-IT job submission script (wsub client)

This script is part of the wsub package. It is a command line client that
allows user to submit and manage jobs.

Requirements: a) Python 2.3 (or later)
              b) connection to the info server (see further down)
              c) wget (only fallback if no SSL support)

Run wsub.py -h or wsub.py --man for help. Please, notice that this will only
work if the requirements are met. Otherwise refer to the online documentation
at http://www.vital-it.ch/.

Author: Bruno Nyffeler, Vital-IT, 2004-06

"""


#==============================================================================
# Import section
#==============================================================================
try:
    import getpass
    import mimetools
    import os
    import signal
    import socket
    import sys
    import tarfile
    import time
    import urllib2
    from optparse import OptionGroup, OptionParser
    from user     import home
except:
    print 'Error: you need Python version 2.3 (or later) to run wsub.py.\n' \
          '       Your current version: %s\n' % sys.version.split()[0]
    raise

try:
    from socket import ssl
except:
    if '--nossl' in sys.argv:
        print 'Wsub without SSL\n'
    else:
        print 'Warning: you do not have SSL support in your Python socket ' \
              'module.\n         Use the --nossl option.\n'



#==============================================================================
# Exception handling
#==============================================================================
class ArgError(SyntaxError):  pass
class AuthError(IOError):     pass
class FileError(IOError):     pass
class Server(IOError):        pass
class Server404(IOError):     pass
class Server500(IOError):     pass
class Server502(IOError):     pass
class UserAbort(IOError):     pass
class UserAuthError(IOError): pass


def pwrap(text, width):
    """Print wrapped text."""

    print reduce(lambda line, word, width=width: '%s%s%s' %
                 (line, ' \n'[(len(line)-line.rfind('\n')-1
                        + len(word.split('\n',1)[0]) >= width)], word),
                 text.split(' '))


def error(msg):
    """Print the error message and exit."""

    pwrap('Wsub%s' % msg, 80)
    Exit(1)


def Exit(code):
    """Exit with code, but flush stdout (since _exit() is not doing it)."""

    sys.stdout.flush()
    os._exit(code)



#==============================================================================
# Global variables (dictionaries)
#
#   prog
#   server
#   url
#   info
#==============================================================================
class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        
    def __getattr__(self, name):
        return self[name]


prog = AttrDict({
    'lastChange': 'May 05, 2010',
    'cmdLine':    ' '.join(sys.argv),
    'lastJob':    os.path.join(home, '.lastwsubjid'),
    'name':       os.path.basename(sys.argv[0]),
    'noscp':      False,
    'nossl':      False,
    'session':    os.path.join(home, '.wsubsession'),
    'verbose':    False,
    'version':    1.0,
    #'wgetOpts':   ''
    'wgetOpts':   '--no-check-certificate'
    })
    
server = AttrDict({
    'auth':     None,
    'host':     None,
    'noauth':   False,
    'promptpw': 0,
    'user':     os.environ.get('WSUBUSER', getpass.getuser())
    })

url = AttrDict({
    'info':    'http://www.vital-it.ch/prd/www/cgi-bin/Wserver?mode=info',
    'server':  'http://www.vital-it.ch/%s/%s/cgi-bin/Wserver',
    'serverS': 'https://www.vital-it.ch/%s/%s/cgi-bin/Wserver',
    'wsub':    'https://svn.vital-it.ch/svn/wsub/trunk/wsub/wsub.py'
    })

info = AttrDict({})
try:
    # set a short timeout to retrieve information from the server
    socket.setdefaulttimeout(5)
    webinfo = urllib2.urlopen(url.info).readlines()
    socket.setdefaulttimeout(None)

    try:
        for l in map(lambda l: l[:-1].split(' '), webinfo):
            info[l[0]] = l[1:]
        info.contact    = info.contact[0]
        info.motd       = ' '.join(info.motd).replace('\\\\', '\n')
        info.uploadhost = info.uploadhost[0]
        info.uploadpath = info.uploadpath[0]
        info.version    = float(info.version[0])
    except:
        raise
        error('[connect]: server information corrupted.')
        
    
except:
    #raise
    error('[connect]: program cannot be run. No contact to information ' \
          'server: %s\nPlease, contact the administrators.\n' % url.info)


#==============================================================================
# User documentation
#
# The manual page needs some information from the server. It will not display
# if there is no connection.
#==============================================================================
class help:
    rep = (prog.name,)*2 + ('|'.join(info.hostlist),)*2 \
        + (info.hostlist[0], server.user, \
           '|'.join(info.arch), 'none', \
           '|'.join(info.para), info.para[0], \
           '|'.join(info.queues), info.queues[0]) \
        + (prog.name,)*10 + (prog.version, info.contact, prog.lastChange)
    msg = """
NAME
       %s - submit a job to the Vital-IT clusters\n
SYNOPSIS
       %s [ -hjJpVv ] [ --man ] [ --update=FILE ]
               [ --auth=USER ] [ --host=%s ] [ --jid=JID ] [ --user=USER ]
               [ --noauth ] [ --noscp ] [ --nossl ] [ --promptpw ]
               [ --dest=FILE|PATH ] [ --follow ] [ --get ] [ --peek=FILE ]
               [ --status ]
               [ --delete ] [ --restart ] [ --resume ] [ --stop ] [ --suspend ]
               [ --arch=ARCH ] [ --email=ADDRESS ] [ --import=FILE ]
               [ --in=FILE ] [ --jobname=STRING ]
               [ --nodes=N[+] ] [ --out=file ] [ --para=STRING ]
               [ --preexec=STRING ] [ --queue=STRING ]
               [ --command=]\"command [args ...]\"\n
DESCRIPTION
       Submit a command with arbitrary arguments to a Vital-IT cluster using N
       to MAX nodes. Files to up- or download before resp. after job execution
       may be specified. A job identifier is given to the user which allows to
       manipulate the job (ie. retrieve results, kill the job, check status).
       It is possible to \'follow\' the job which redirects the standard output
       and error to the calling shell (ie. like starting the job locally on
       the shell).\n
OPTIONS
       General options

         -h    shows a short help page.\n
         -j    like --jid\n
         -J    performs all actions on the lastly submitted job (this may be
               used instead of --jid). Handle with care.\n
         -p    like --promptpw\n
         -V    is a little more descriptive about what is being done.\n
         -v    print version number.\n
         --man
               prints this help page\n
         --update=FILE
               specify a (non-existing) filename FILE to which the latest
               version of wsub.py will be downloaded.\n

       Server options (identification of host, user and job)\n
         --auth=USER
               authenticate using a different users' credentials (eg. an admin
               wants to run some tests as a certain user). This works for admin
               accounts only.\n
         --host=%s
               choose the cluster to execute your job on (default: %s).\n
         --jid=JID
               If this (numerical) JID is given all actions are performed on
               this (existing) job. Do not specify if submitting a new job.\n
         --user=STRING
               while STRING is the name of your user account on Vital-IT
               ressources (default: \'%s\').
               The script will ask interactively for a password. To prevent
               this (eg. for automatical job submission), assign the valid
               password to the environment variable \'WSUBPASS\'.\n

       Authentication\n
         --noauth
              do not prompt for a password assuming that the user is allowed
              to proceed without authentication.\n
         --noscp
              do not use scp to upload files, but directly in the
              HTTP request (slower). See COMPATIBILITY for more information.\n
         --nossl
              replace SSL request by a wget request. This option will be
              omitted in future releases. See COMPATIBILITY for more
              information.\n
         --promptpw\n
              prompts for a password instead of printing an authentication
              error message (only while uploading files using --in).\n

       Job output (requires a valid job ID)\n
         --dest=FILE|PATH
               saves whatever is downloaded either in the specified (not
               existing) FILE (in tarzipped format) or extracts it into the
               directory PATH.\n
         --follow
               follows the output of job JID, ie. the output of the job is
               redirected to the calling terminal. This option allows you to
               retrieve results in realtime (almost, because apache webserver
               does its own buffering).\n
         --get
               returns the results of an already finished job.\n
         --peek=FILE
               all specified FILEs in their current state will be returned
               (this allows to check log files or the jobs' progress).\n

       Job status\n
         --status
               if an JID is specified the current status of the job will be
               returned. Otherwise, a status page of all jobs will be
               displayed.\n

       Job control (requires a valid job ID)\n
         --delete
               the working directory (containing all temporary, input and
               output files) and the file containing the results are deleted.
               This should only be done for all jobs which have finished and
               the results have been downloaded.\n
         --restart
               restarts an existing job under a new JID (does not affect the
               existing job).\n
         --resume
               continues execution of a previously suspended job.\n
         --stop
               stops a running or pending job. All temporary or resulting files
               can be still downloaded, but the job cannot be resumed again.\n
         --suspend
               stops a job temporarily (eg. to allow other jobs to run). The
               job can be continued with \'--resume\'.\n

       Job Submission\n
         --arch=%s
               choose the architecture to run the job on (default: %s).\n
         --email=ADDRESS
               if specified, an e-mail will be sent upon job completion.\n
         --import=FILE
               allows you to use files that are only present on the master node
               but not on the computation nodes of the cluster.\n       
         --in=FILE
               specify one input file needed by \'command\'. Multiple input
               files require multiple \'--in\' arguments.\n
         --jobname=STRING
               a descriptive name (up to ten characters) to easily recognize
               the job in the cluster status (default is \'wsubjob.sh\').\n
         --memory=N
               This option does not work anymore. Please use --arch instead.\n
         --nodes=N[+]
               number of nodes to run the job on. If nodes greater than 1,
               \'command\' must be an parallel program. If '+' is specified,
               all available nodes will be used to run the job.\n
         --out=file
               specify one output file produced by \'command\'. Every file has
               to be listed seperately.\n
         --para=%s
               choose the parallel interface to use (default: %s).\n
         --preexec=STRING
               a command to be run before the main command. Useful for parallel
               computations.\n
         --queue=%s
               choose the queue to run the job on (default: %s).\n

       [ --command=]\"command [args ...]\"
               a command to submit to the cluster chosen with --host. The whole
               command line must be put between quotes (\"\").\n
EXAMPLES
       Easy example to get the hostname of the execution host (as default user
       \'www\'):\n
           %s \"hostname\"\n
       Run the MPI version of clustalW, using \'test.seq\' as an input file and
       retrieve both output files \'test.aln\' and \'test.dnd\':\n
           %s --para=mpich --nodes=3 \\
                --in=test.seq --out=test.aln --out=test.dnd \\
                \"clustalw-mpi -infile=test.seq\"\n
       Run a simple job and send an email upon job completion:\n
           %s --email=user@host.ch --out=out.txt \\
               \"sleep 30; uname -a > out.txt\"\n
       Show the the status of jobs of the cluster \'prd\':\n
           %s --host=prd --status\n
       Stop a job and delete its entire output with its identifier:\n
           %s --jid=1234 --stop; %s --jid 1234 --delete\n
       Download the file \'out.txt\' of a currently running job:\n
           %s --jid=1234 --peek=out.txt\n
       Display standard output and error and download the output files of a
       finished job (as if it has been locally):\n
           %s --jid=1234 --get\n
       Download the tarball of all results (including standard output and
       error) to file \'results.tgz\':\n
           %s --jid=1234 --get --dest=results.tgz\n
       Download the latest version of the client script to file \'latest.py\':

           %s --update=latest.py\n
AUTHENTICATION
       There are two authentication steps when submitting a job:\n
       1. authentication on the execution host: in order to start a job on a
          Vital-IT cluster the user has to submit his/her password each time.
          In most cases (eg. batch job submission) it is not feasible to enter
          the password manually. Thus, the password may be stored in the
          environment variable WSUBPASS, eg. using a shell command like:\n
             export WSUBPASS=\"myPassword\"\n
          Be aware that your password is not encrypted, so either close the
          shell or unset the environment variable afterwards.\n
       2. authentication on the data repository: to upload data (using the --in
          option) you must be able to log onto the data repository without
          having to use a password (or use option -p and enter the password
          manually). If not, an authentication error including some detailed
          instructions will show up.\n
       In special cases it is possible to circumvent authentication: the
       administrators can allow access without password from a certain host.
       This is useful in cases where wsub is used in workflows or as backend of
       a web service (also check section COMPATIBILITY). In these cases use
       the following options:\n
         --noauth
               Gives the user access without a password. This is usually used
               by services using wsub as a backend and works only for certain
               pairs of users and hosts for which 'host-based authentication'
               has been configured. Ask the admins for more information.\n
COMPATIBILITY
       There are two additional options which allow usage of the script even
       without SSL and SCP support:\n
         --nossl
               On some platforms or on systems with old python versions there
               is no SSL support, thus it is not possible to contact the
               authentication server (https). Wsub will print a warning if it
               detects the problem. With the option --nossl wsub will try
               to get the necessary information using wget (so make sure it is
               installed). WARNING: it is not recommended to use this option
               (especially not together with --noscp). You should rather
               update your Python installation.\n
         --noscp
               Some users have no possibility to secure copy (scp) files since
               they have no home directory (eg. apache). Using this option wsub
               is uploading all input files directly in the HTTP header. This
               will slow down the job submission.
ERRORS
       The job's standard output and error are redirected into files std.out
       and std.err. Use --get (if job has already finished) or --follow to
       redirect them to the calling shell. This way, job errors are displayed
       as if the job was executed locally. The error codes (and messages) of
       the server script are printed to standard output. However, the exit
       code of the client script will almost ever be 0.\n
VERSION
       This is version %s. The option \'-v\' prints the actual program version.
       If a new version is available, the program will print a short message.\n
BUGS
       In case of error, try to execute the same command using option \'-V\'
       and report the error including all output and your command line to:
       %s\n
AUTHOR
       Bruno Nyffeler, Vital-IT, SIB
       %s\n""" % rep



#==============================================================================
# class InputParser
#==============================================================================
class InputParser:
    """Parse command line arguments, return a dictionary containing all info.

    This class parses the command line arguments and translates them in a
    dictionary that servers as input for the JobSender class. There is only
    the parse() method to be called from outside. parse() will call
    _parseArgs() and _evaluateOptions() and returns the dictionary.

    """

    #--------------------------------------------------------------------------
    # public
    #
    #    parse()
    #--------------------------------------------------------------------------
    def parse(self):
        self._parseArgs()
        return self._evaluateOptions()


    #--------------------------------------------------------------------------
    # private
    #
    #    _parseArgs()
    #    _checkList(arg, list)
    #    _evaluateOptions()
    #--------------------------------------------------------------------------
    def _parseArgs(self):
        """Parse command line arguments.

        This method makes use of Python's OptionParser. It parses the
        command line and creates the variable self.options (storing all the
        command line arguments chosen by the user) and self.command
        (containing the submitted command).

        """
        
        parser = OptionParser(usage='%prog [options] ["command"]')

        # tasks that do not interact with the server
        parser.add_option('-V', '--verbose',
                          dest='verbose',
                          action='store_true',
                          help='be a little more talkative')
        parser.add_option('-v', '--version',
                          dest='version',
                          action='store_true',
                          help='show program version')
        parser.add_option('--man',
                          action='store_true',
                          help='display a more detailed help page')
        parser.add_option('--update',
                          dest='update',
                          metavar='FILE',
                          help='download latest wsub.py version to FILE')

        # options that affect all client actions
        gGeneral = OptionGroup(parser, 'IDENTIFICATION')
        gGeneral.add_option('--auth',
                            dest='auth',
                            metavar='USER',
                            help='authenticate as a different user (only ' \
                            'admin users will work)')
        gGeneral.add_option('--host',
                            dest='host',
                            default=info.hostlist[0],
                            metavar='HOST',
                            help='cluster to execute the job on (default: %s)'\
                            % info.hostlist[0])
        gGeneral.add_option('--user',
                            dest='user',
                            default=server.user,
                            metavar='USER',
                            help='account used to submit job (default: %s)' \
                            % server.user)
        gGeneral.add_option('-j', '--jid',
                            dest='jid',
                            type='int',
                            help='job ID to perform actions on (not to be ' \
                            'specified when submitting new jobs)')
        gGeneral.add_option('-J',
                            dest='lastjid',
                            action='store_true',
                            help='perform actions on last submitted job')
        parser.add_option_group(gGeneral)

        # options needed for authenticating the client on the server
        gAuth = OptionGroup(parser, 'AUTHENTICATION')
        gAuth.add_option('--noauth',
                         dest='noauth',
                         action='store_true',
                         help='do not prompt for password assuming that ' \
                         'the user is allowed to proceed without ' \
                         'authentication')
        gAuth.add_option('--noscp',
                         action='store_true',
                         help='do not use scp to upload files, but ' \
                         'directly in the HTTP request (slower)')
        gAuth.add_option('--nossl',
                         action='store_true',
                         help='replace SSL request by a wget request. Be ' \
                         'careful and read the man page.')
        gAuth.add_option('-p', '--promptpw',
                         dest='promptpw',
                         default=0,
                         action='store_const',
                         const=1,
                         help='prompt for password rather than showing an ' \
                         'error message')
        parser.add_option_group(gAuth)

        # getting output from an existing jobs
        gOutput = OptionGroup(parser, 'OUTPUT')
        gOutput.add_option('--dest',
                           dest='dest',
                           metavar='FILE|PATH',
                           help='save output as tarzip FILE or extract it ' \
                           'to PATH')
        gOutput.add_option('--follow',
                           dest='follow',
                           action='store_true',
                           help='retrieve job results in (almost) realtime')
        gOutput.add_option('--get',
                           dest='get',
                           action='store_true',
                           help='returns the results of a finished job')
        gOutput.add_option('--peek',
                           dest='peek',
                           default=[],
                           action='append',
                           metavar='FILE',
                           help='returns FILE of a job in its current state')
        parser.add_option_group(gOutput)

        # getting information about existing jobs
        gStatus = OptionGroup(parser, 'JOB STATUS')
        gStatus.add_option('--status',
                           dest='status',
                           action='store_true',
                           help='return current job status or a status page ' \
                           'of all running jobs')
        parser.add_option_group(gStatus)

        # changing status of existing jobs
        gManage = OptionGroup(parser, 'JOB MANAGEMENT',  \
                              '(all these require a valid job ID)')
        gManage.add_option('--delete',
                           dest='delete',
                           action='store_true',
                           help='delete all data of specified job')
        gManage.add_option('--restart',
                           dest='restart',
                           action='store_true',
                           help='restart a job using a new job ID')
        gManage.add_option('--resume',
                           dest='resume',
                           action='store_true',
                           help='continue execution of a suspended job')
        gManage.add_option('--stop',
                           dest='stop',
                           action='store_true',
                           help='stop running or pending job')
        gManage.add_option('--suspend',
                           dest='suspend',
                           action='store_true',
                           help='stop a job temporarily')
        parser.add_option_group(gManage)

        # options that describe a new job being submitted
        gSubmit = OptionGroup(parser, 'JOB SUBMISSION')
        gSubmit.add_option('--arch',
                           dest='arch',
                           metavar='ARCH',
                           help='architecture to run the job on')
        gSubmit.add_option('--email',
                           dest='email',
                           metavar='ADDRESS',
                           help='an email will be sent to ADDRESS upon job ' \
                           'completion')
        gSubmit.add_option('--import',
                           dest='importFile',
                           default=[],
                           action='append',
                           metavar='FILE',
                           help='import a remote FILE to the working dir')
        gSubmit.add_option('--in',
                           dest='inFile',
                           default=[],
                           action='append',
                           metavar='FILE',
                           help='upload a local FILE')
        gSubmit.add_option('--jobname',
                           dest='jobname',
                           default='wsubjob.sh',
                           metavar='STRING',
                           help='descriptive name to easily recognize the job'\
                           ' in the status page (default: \'wsubjob.sh\')')
        gSubmit.add_option('--nodes',
                           dest='nodes',
                           default='1',
                           metavar='N[+]',
                           help='use N (or more if \'+\' is added) between N '\
                           'and MAX) number of CPUs to run the job (if N > 1,'\
                           ' \'command\' must be an MPI program)')
        gSubmit.add_option('--out',
                           dest='outFile',
                           default=[],
                           action='append',
                           metavar='FILE',
                           help='include FILE to resulting output')
        gSubmit.add_option('--para',
                           dest='para',
                           metavar='STRING',
                           help='choose parallel interface (default: %s)' \
                           % info.para[0])
        gSubmit.add_option('--preexec',
                           dest='preexec',
                           default='',
                           metavar='STRING',
                           help='command(s) to be run before main command.' \
                           'Useful for parallel jobs (to set environment or'\
                           ' change directory).')
        gSubmit.add_option('--queue',
                           dest='queue',
                           metavar='STRING',
                           help='choose the queue (default: %s)' \
                           % info.queues[0])
        gSubmit.add_option('--command',
                           dest='command',
                           default='',
                           metavar='STRING',
                           help='command(s) being submitted')
        parser.add_option_group(gSubmit)

        self.options, com = parser.parse_args()

        if len(com) > 0:
            if len(self.options.command) > 0:
                raise ArgError, 'two commands were specified, one using ' \
                      '--command. Please, merge commands into one string.'
            self.command = ' '.join(com)
        else:
            self.command = self.options.command


    def _checkList(self, argument, list):
        """Checks if list contains argument, raises an error otherwise."""
        
        if argument is None: return None
        if argument in list: return argument
        raise ArgError, 'unknown argument \'%s\'! Must be one of %s.' \
              % (argument, '|'.join(list))
    

    def _evaluateOptions(self):
        """Examines user options and returns a dict or takes action if needed.

        This is the method within InputParser that evaluates the user input and
        creates the input data for the JobSender class. The input is checked
        and in case of inconsistencies or usage errors it will notify the user.
        
        """

        # print server messages, if any
        if len(info.motd) > 0:
            print '%s\nMESSAGE FROM WSUB SERVER:\n\n%s\n%s\n' \
                  % ('#'*79, info.motd, '#'*79)

        # check for a more recent wsub version
        if info.version > prog.version:
            print '%s\n     NEW WSUB VERSION %s AVAILABLE.\n%s\n' \
                  % ('='*79, info.version, '='*79)

        # options that change the client's behavior only
        server.noauth   = self.options.noauth
        server.promptpw = self.options.promptpw
        prog.verbose    = self.options.verbose
        prog.noscp      = self.options.noscp
        prog.nossl      = self.options.nossl
        if self.options.man:
            # print the manual
            sys.stdout.write(help.msg)
            Exit(0)
        if self.options.update is not None:
            # download the latest update of the client software
            filename = self.options.update
            if os.path.exists(filename):
                raise ArgError, 'file \'%s\' already exists!' % filename
            try:
                open(filename, 'w').write(urllib2.urlopen(url.wsub).read())
                print 'Downloaded update to file \'%s\'.' % filename
            except:
                raise ArgError, 'download did not work. You may download the' \
                      ' update directly from: %s' % url.wsub
            Exit(0)
        if self.options.version:
            # only print the version number
            if prog.verbose:
                print '%s: %1.2f\nPython: %s\n' % (prog.name, prog.version, \
                                                   sys.version)
            else:
                print prog.version
            Exit(0)

        # general settings (check if --host was valid, and set the user and
        #                   the auth user)
        server.host = self._checkList(self.options.host, info.hostlist)
        server.user = self.options.user
        server.auth = self.options.auth

        # options that will be sent to the server (CGI)
        args = {'version': '%1.2f' % prog.version}
        
        args['jobid'] = self.options.jid
        if args['jobid'] is None and self.options.lastjid:
            # if option -J was specified (user gives no job ID, but refers
            # to the most recent job), we get the ID from a file.
            try:
                args['jobid'] = int(open(prog.lastJob, 'r').read())
                print 'job ID: %s' % args['jobid']
            except: pass

        if prog.verbose: print 'Command:', self.command
        if self.command is None or len(self.command.strip()) < 1:
            # if the user did not submit a command, we are either in ...
            # ... management mode
            manage = None
            if self.options.delete:  manage = 'delete'
            if self.options.stop:    manage = 'stop'
            if self.options.restart: manage = 'restart'
            if self.options.suspend: manage = 'suspend'
            if self.options.resume:  manage = 'resume'
            if manage is not None:
                args[manage]  = '0'
                if args['jobid'] is None:
                    raise ArgError, 'valid job ID needed for ' \
                          'management actions.'
                if manage == 'restart': args['mode'] = 'submit'
                else:                   args['mode'] = 'manage'
                return args

            # ... or status mode
            if self.options.status is not None:
                args['mode']  = 'status'
                args['qstat'] = (args['jobid'] is None)
                return args

            # ... or output mode
            if self.options.follow or self.options.get or \
                   self.options.peek != []:
                if args['jobid'] is None:
                    raise ArgError, 'valid job ID needed for output actions.'

                args['dest']   = self.options.dest
                args['follow'] = self.options.follow
                args['get']    = self.options.get
                args['mode']   = 'output'
                args['peek']   = ' '.join(self.options.peek)
                return args

            # ... or else it happened by mistake.
            raise ArgError, 'command is empty'

        # if we get this far, the user wanted to submit a job
        # First we check whether input files exist, ...
        for file in self.options.inFile:
            if file != '' and not os.path.exists(file):
                raise ArgError, 'file \'%s\' does not exist!' % file
        # ... if the number of nodes was a number ...
        if not self.options.nodes.rstrip('+').isdigit():
            raise ArgError, 'nodes must be an int (with an optional \'+\')!'
        # ... whether a job ID was given by mistake.
        if args['jobid'] is not None:
            raise ArgError, 'no ID allowed when submitting a new job!'

        # all other options are stored in the output dict (some after a check)
        args['arch']     = self._checkList(self.options.arch, info.arch)
        args['command']  = self.command
        args['dest']     = self.options.dest
        args['email']    = self.options.email
        args['follow']   = self.options.follow
        args['jobid']    = abs(hash(time.time()))
        args['jobname']  = self.options.jobname
        args['mode']     = 'submit'
        args['para']     = self._checkList(self.options.para, info.para)
        args['preexec']  = self.options.preexec
        args['nodes']    = self.options.nodes
        args['queue']    = self._checkList(self.options.queue, info.queues)

        args['import']   = ' '.join(self.options.importFile)
        args['in']       = ' '.join(self.options.inFile)
        args['out']      = ' '.join(self.options.outFile)
        return args



#==============================================================================
# class JobSender (and related subroutine)
#==============================================================================
class JobSender:
    """Initialize connection to server and submit user query.

    The JobSender class needs to be called in a specific order: init() should
    be called, which either returns (if successful) or abort with an exception.
    After that submit() should be called with a valid dict of arguments (as
    produced by class InputParser. This will return an output stream to the
    server.
    
    """
    
    #--------------------------------------------------------------------------
    # public
    #
    #    init([limit])
    #    submit(args)
    #--------------------------------------------------------------------------
    def init(self, limit=3):
        """This method takes care of authenticating the user on the server.

        There are two levels of authentication. First, we try to find a
        session ID from previous runs and see whether it is still valid.
        Second, we read a password either from the environment variable
        WSUBPASS or from standard input.
        In case of success, a new session is opened and its ID is written to
        a file.
        Otherwise, we will retry until success or a limit is reached.

        """

        # which user should be authenticated (this is to allow super-users)
        if server.auth is None: self.authuser = server.user
        else:                   self.authuser = server.auth

        # check for an old session and try to validate it
        session = self._readSessionID()
        if session != '':
            result = self._sendQuery({'mode':    'auth', \
                                      'authuser': self.authuser, \
                                      'session':  session}).read()
            if result.find('invalid') == -1:
                self.session = result
                self._writeSessionID(self.session)
                return

        # if option --noauth is set, we assume that 'host authentication'
        # on the server is activated, i.e. the user may send an arbitrary
        # password (eg. 'x') and needs only one attempt
        firstPass = None
        if server.noauth:
            firstPass = 'x'
            limit = 1

        # get the password from env or stdin and try to validate it.
        authpass = os.environ.get('WSUBPASS', firstPass)
        while limit > 0:
            if authpass is None or authpass == '':
                save = sys.stdout
                try:
                    sys.stdout = open('/dev/tty', 'w')
                except:
                    pass
                sys.stdout.write('%s@%s\'s password: ' \
                                 % (self.authuser, server.host))
                sys.stdout.flush()
                authpass = getpass.getpass('')
                sys.stdout = save
                
            result = self._sendQuery({'mode':    'auth', \
                                      'authuser': self.authuser, \
                                      'authpass': authpass},secure=True).read()
            if prog.verbose: print "--------------------->>>", result

            if result.find('invalid') == -1:
                self.session = result
                self._writeSessionID(self.session)
                return
            authpass = None
            limit -= 1

        # no authentication
        if limit == 0: raise UserAuthError, self.authuser


    def submit(self, args):
        """Form the query for job submission."""

        def _onSignalAbort(sig, stack): raise UserAbort
        
        args['authuser'] = self.authuser
        args['session']  = self.session
        args['full']     = prog.cmdLine
        if args['mode'] == 'submit':
            signal.signal(signal.SIGINT, _onSignalAbort)
        return self._sendQuery(args)


    #--------------------------------------------------------------------------
    # private
    #
    #    _readSessionID()
    #    _writeSessionID(session)
    #    _uploadFile(file, username, jobID)
    #    _getDisp(key, value[, content])
    #    _encodeJob(args)
    #    _sendQuery(args[, secure])
    #--------------------------------------------------------------------------
    def _readSessionID(self):
        try:    return open(prog.session, 'r').readlines()[0].strip()
        except: return ''


    def _writeSessionID(self, session):
        try:    open(prog.session, 'w').write(session)
        except: pass


    def _uploadFile(self, file, username, jobID):
        """Upload a File to the file repository (on the upload host) using scp.
        
        This method calls scp (using popen) and uploads a file belonging to a
        certain job jobID to the general data repository (into the upload path
        on upload host). The target file name contains the username, the job
        ID and the original file's name.
        This method will be only called by the JobSender's encodeJob() method.

        Important: the user needs to be able to scp without password.
        
        """

        repos   = '%s@%s:%s/' % (username, info.uploadhost, info.uploadpath)
        tmpfile = '%s.%s.%s' % (server.user, jobID, os.path.basename(file))
        scpOpts = '-o NumberOfPasswordPrompts=%s ' % server.promptpw \
                  + '-o UsePrivilegedPort=no'
        scpcom  = 'scp %s %s %s%s' % (scpOpts, file, repos, tmpfile)
        if prog.verbose: print 'uploading file \'%s\'\n%s' % (file, scpcom)
        try:
            shell  = os.popen(scpcom, 'r')
            output = shell.read()
            if shell.close() is not None: raise
        except:
            raise AuthError, exit


    def _getDisp(self, key, value, content = None):
        """Return a proper content disposition entry for HTTP header."""
        
        s = 'Content-Disposition: form-data; '
        if content: return ['%s name="%s"; filename="%s"' % (s, key, value),
                            'Content-Type: application/octet-stream', '', \
                            content]
        else:       return ['%s name="%s"' % (s, key), '', str(value)]


    def _encodeJob(self, args):
        """mime encode the arguments.

        The arguments from InputParser need to be encoded properly. The options
        --in, --out and --import can have multiple entries, so we need to
        expand them. In some cases (--noscp) we also need to upload the
        content of the input files.

        """

        # Filter empty arguments and expand options with multiple values
        expandedArgs = []
        for (key, value) in args.items():
            if value is None or value == '' or value == False: continue
            if key in ['in', 'out', 'import']:
                for v in value.split(' '):
                    if v != '': expandedArgs.append((key, v))
            else: expandedArgs.append((key, value))

        # Form HTTP header and add contents of input files if necessary
        boundary = mimetools.choose_boundary()
        L        = []
        for (key, value) in expandedArgs:
            L.append('--' + boundary)
            if key != 'in': L += self._getDisp(key, value)
            else:
                if prog.noscp:
                    content = open(value, 'r').read()
                else:
                    content = None
                    self._uploadFile(value, self.authuser, args['jobid'])
                L += self._getDisp(key, os.path.basename(value), content)
        L.append('--' + boundary + '--')
        L.append('')

        return 'multipart/form-data; boundary=%s' % boundary, '\r\n'.join(L)


    def _sendQuery(self, args, secure = False):
        """Send a HTTP query to the server cgi script using urllib2 or wget."""
        
        if secure: addr = url.serverS % (server.host, server.user)
        else:      addr = url.server  % (server.host, server.user)
        
        contentType, data = self._encodeJob(args)
        headers = {'Content-Type': contentType,
                   'Content-Length': str(len(data))}
        req = urllib2.Request(addr, data, headers)
        
        if prog.verbose: print "URI: %s?%s" % (addr, data)

        if secure and prog.nossl:
            # wget cannot use the encoded data string, so we redo it
            data = '&'.join(map(lambda a: '%s=%s' % a, args.items()))
            
            command = 'wget %s -qO - "%s?%s"' % (prog.wgetOpts, addr, data)
            if prog.verbose: print "Using wget:", command
            return os.popen(command)

        try:
            return urllib2.urlopen(req)
        except:
            raise Server404



#==============================================================================
# class OutputParser
#==============================================================================
class OutputParser:
    """Read the output stream, parse for errors and procude appropriate output.

    This class just offers method handle(). It has to called with an open
    stream, the follow flag and the output destination.

    """
    
    #--------------------------------------------------------------------------
    # public
    #
    #     handle(stream, follow, dest)
    #--------------------------------------------------------------------------
    def handle(self, stream, follow, dest):
        """Handle the output stream from the server.
        
        Examines data coming from stream, checks whether it contains error
        messages or unpacks it, if in proper format. If the user wants to
        follow the output, it provides functionality like UNIX command 'tail'.

        """
        
        code = 0
        if follow:
            # print output as it is generated until end tag is detected
            jobID = int(stream.readline())
            line  = None
            while True:
                line = stream.readline()
                if not line: break
                # each line starts with a one character number, meaning:
                # '0': regular output, print the rest of the line
                # '1': just a ping to keep connection alive
                # '2': end of output
                if line[0] == '0': print line[1:],
                if line[0] == '2': break

            try:
                code = int(line[1:])
                if prog.verbose: print 'Exit code: ', code
            except:
                print 'Cannot parse exit code:', line

        # the output is either a complete tarball containing the results, a
        # html file containing web server errors or just a simple integer
        # job ID. Otherwise, it's too strange and we just print it and let the
        # user decide.
        output = stream.read()
        if self._isGzip(output): self._handleTgz(output, follow, dest, code)
        self._checkForError(output)
        if output.isdigit() and len(output) < 12:
            try:    open(prog.lastJob, 'w').write(output)
            except: raise
            if prog.verbose: print 'Job %s has been submitted.' % output
            else:            print output
        else:
            print output

        Exit(code)
        
    
    #--------------------------------------------------------------------------
    # private
    #
    #     _isGzip(data)
    #     _checkForError(output)
    #     _handleTgz(output, follow[, dest])
    #--------------------------------------------------------------------------
    def _isGzip(self, data):
        """Simple test whether data is in gzip format."""
        
        return len(data) > 1 and ord(data[0]) == 31 and ord(data[1]) == 139


    def _checkForError(self, output):
        """Parse output for common web errors."""
        
        if output.upper().find('<!DOCTYPE HTML PUBLIC') > -1:
            # a) a error on the server 
            if output.find('500 Internal Server Error') > -1:
                raise Server500
            # b) unable to connect to server
            if output.find('Object not found!') > -1 or \
                   output.find('404 Not Found') > -1:
                raise Server404
            # c) bad gateway
            if output.upper().find('BAD GATEWAY') > -1 or \
                   output.find('Error 502') > -1:
                raise Server502

        # It could be a server error
        if output.find('Error(') > -1: raise Server, output


    def _handleTgz(self, output, follow, dest = None, exitCode = 0):
        """Unpack and/or store the output tarball.

        If dest is a filename, the whole output will be saved to this file
        unaltered. The file must not exist.
        Otherwise, the tarball gets unpacked. If dest is a valid directory,
        the files will be unpacked there. If no destination has been chosen,
        we print everything to standard output. If the user follows the output,
        there is no need to print std.out and std.err again since it has been
        already printed.

        """
        
        if dest is None or os.path.isdir(dest):
            tmpFile = '/tmp/.results.%s' % os.getpid()
            open(tmpFile, 'w').write(output)
            tgz     = tarfile.open(tmpFile, 'r:gz')
            members = tgz.getmembers()
            names   = tgz.getnames()
            if follow:
                names.remove('std.out')
                names.remove('std.err')
            if dest is not None:
                for file in members:
                    if file.name in names: tgz.extract(file, dest)
            else:
                for file in members:
                    if file.name in names:
                        if prog.verbose: print '='*30, file.name, '='*30, '\n'
                        print tgz.extractfile(file).read()
            tgz.close()
            #os.unlink(tmpFile)
        elif not os.path.exists(dest):
            open(dest, 'w').write(output)
            if prog.verbose: print 'Downloaded file \'%s\'.' % dest
        else:
            raise FileError, 'file \'%s\' exists' % dest
        Exit(exitCode)
        




#==============================================================================
# Main
#==============================================================================
input  = InputParser()
sender = JobSender()
output = OutputParser()

try:
    args = input.parse()
    
    sender.init()
    stream = sender.submit(args)

    output.handle(stream, args.get('follow', False), args.get('dest', None))


#------------------------------------------------------------------------------
# Exception messages
#------------------------------------------------------------------------------
except ArgError, msg:
    error('[input]: %s\n\nType wsub.py -h for help.\n' % msg)
except AuthError, msg:
    error('[auth]: Authentication problem: wsub.py assumes that user \'%s\' ' \
          'is allowed to log onto %s without typing a password. You may ' \
          'want to follow these steps:\n' \
          '1. If there is no file \'~/.ssh/id_dsa.pub\' on the host from ' \
          'which you would like to submit, create it using\n' \
          '     ssh-keygen -t dsa (without a pass phrase)\n' \
          '2. Append the public key to the file \'authorized_keys\' on ' \
          '%s using:\n     scp id_dsa.pub %s@%s:\n' \
          '     ssh %s@%s "cat id_dsa.pub >> ~/.ssh/authorized_keys; ' \
          'rm id_dsa.pub"\n' \
          % (server.user, info.uploadhost, info.uploadhost, server.user, \
             info.uploadhost, server.user, info.uploadhost))
except FileError, err:
    error('[file]: %s' % err)
except Server, err:
    error('[server]: %s' % err)
except Server404:
    error('[connect]: the user account \'%s\' could not be found on host \'' \
          '%s\'. Please send this message to: %s\n' \
          % (server.user, server.host, info.contact))
except Server500:
    error('[connect]: the server caused an error. Retry using \'-V\' ' \
          'and send the output as well as the command line to: %s\n' \
          % info.contact)
except Server502:
    error('[connect]: the client received a \'bad gateway\' error. One of ' \
          'the servers seems to be down. Please send this message to: %s\n' \
          % info.contact)
except UserAbort:
    error('[abort]: Aborting shuts down only the client but not the server ' \
          'script. Probably, the job has been started on the cluster already.'\
          ' Check the web status page or use the --status option to see the ' \
          'job status.\n')
except UserAuthError, user:
    error('[auth]: Could not authenticate user \'%s\'.\n' % user)