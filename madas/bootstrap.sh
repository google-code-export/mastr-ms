#!/bin/bash

#
# Its a sample script, tested only to the point of running manage.py runserver_plus
#
# You need to have:
#   python header files 
#   postgres headers
#   ldap header
#   sasl header files

EGGS_DIR='eggs/'
EGGS_PATTERN='*.*' #this ignores dirs, but means egg names must contain a .
PIP_DOWNLOAD_CACHE='/tmp/'
export PIP_DOWNLOAD_CACHE
INSTALL_EGGS=1 #if this is 1, we will install eggs from eggs/...
CONFIG_DIR=""
TARGET_PYTHON="python"

help() {
    echo >&2 "Usage $0 [-p targetpython] [-c configname]"
            echo >&2 "target python is the interpreter you want your virtual python to be based on (default=python)"
            echo >&2 "configname is the name of a subdir of eggs containing custom eggs for your environment"
            exit 1;
    
}

if [ $# -eq 1 ]
then
    help;
fi

#parse command line options
while getopts p:c: opt
do case "$opt" in 
    p)      TARGET_PYTHON="$OPTARG";;
    c)      CONFIG_DIR="$OPTARG";;
    [?]|*)  help;; 
    esac
done

#First, lets check to see if the config dir exists
EGGS_PATH="$EGGS_DIR$CONFIG_DIR/$EGGS_PATTERN"
if [ ! -d $EGGS_DIR$CONFIG_DIR ]
then
    if [ "$CONFIG_DIR" != "" ]
    then
        echo "No such configuration path exists: $EGGS_PATH"
        if [ -d $EGGS_DIR ]
        then    
            echo "Perhaps try one of these:"
            cd $EGGS_DIR
            for arg in *
            do
                if [ -d $arg ]
                then
                    echo "$arg"
                fi
            done
        cd ..
        fi
        echo "Explicit config $CONFIG_DIR given but didn't exist - exiting"
        exit
    else
        echo "No eggs dir found, proceeding with bare install."
        INSTALL_EGGS=0
    fi
fi



if [ $INSTALL_EGGS -eq 1 ]
then
    echo "---+++---"
    echo "Building for eggs in $EGGS_PATH"
    if [ -f $EGGS_DIR$CONFIG_DIR/DEPENDENCIES ]
    then
        cat $EGGS_DIR$CONFIG_DIR/DEPENDENCIES
    fi    
    echo "---+++---"
fi

BASE_DIR=`basename ${PWD}`
PRE="virt_"
VPYTHON_DIR="$PRE$BASE_DIR"
VIRTUALENV='virtualenv-1.6.1'
VIRTUALENV_TARBALL='virtualenv-1.6.1.tar.gz'

# only install if we dont already exist
if [ ! -d $VPYTHON_DIR ]
then
    echo -e '\n\nNo virtual python dir, lets create one\n\n'

    # only install virtual env if its not hanging around
    if [ ! -d $VIRTUALENV ]
    then
        echo -e '\n\nNo virtual env, creating\n\n'
  
        # only download the tarball if needed
        if [ ! -f $VIRTUALENV_TARBALL ]
        then
            wget http://pypi.python.org/packages/source/v/virtualenv/$VIRTUALENV_TARBALL
        fi

        # build virtualenv
        tar zxvf $VIRTUALENV_TARBALL
        cd $VIRTUALENV
        $TARGET_PYTHON setup.py build
        cd ..

    fi
       
    # create a virtual python in the current directory
    $TARGET_PYTHON $VIRTUALENV/build/lib*/virtualenv.py --no-site-packages $VPYTHON_DIR

    # we use fab for deployments
    ./$VPYTHON_DIR/bin/pip install fabric

    # install Mercurial
    ./$VPYTHON_DIR/bin/pip install mercurial

    # install all the eggs in this app
    if [ $INSTALL_EGGS -eq 1 ]  
    then
        ./$VPYTHON_DIR/bin/easy_install $EGGS_PATH --allow-hosts=None
    fi
    # now we are going to eggify app settings, so we can run it locally
    # we need to jump through a few legacy hoops to make this happen

    #remove temp dir
    if [ -d tmp ]
    then
        rm -Rf tmp
    fi

    mkdir tmp
    cd tmp
    rm -rf ccgapps-settings 
    svn export svn+ssh://ccg.murdoch.edu.au/store/techsvn/ccg/ccgapps-settings
    # the directory has the wrong name, so create a sym link with the name we need
    ln -s ccgapps-settings appsettings
    # the setup.py is at the wrong level
    mv appsettings/setup.py .
    ../$VPYTHON_DIR/bin/python setup.py bdist_egg
    ../$VPYTHON_DIR/bin/easy_install dist/*.egg
    rm -rf appsettings ccgapps-settings 
    cd ..

    #remove temp dir
    if [ -d tmp ]
    then
        rm -Rf tmp
    fi

    # hack activate to set some environment we need
    echo "PROJECT_DIRECTORY=`pwd`;" >>  $VPYTHON_DIR/bin/activate
    echo "export PROJECT_DIRECTORY " >>  $VPYTHON_DIR/bin/activate
    
    #if we have env stuff in an ENVIRONMENT file, source it. It should
    #be coded to hack more stuff onto the end of activate
    if [ -f $EGGS_DIR$CONFIG_DIR/ENVIRONMENT ]
    then
        source $EGGS_DIR$CONFIG_DIR/ENVIRONMENT
    fi
fi

echo -e "\n\n What just happened?\n\n"
echo " * Python has been installed into $VPYTHON_DIR"
if [ $INSTALL_EGGS -eq 1 ]
then
    echo " * eggs from the eggs in this project ($EGGS_PATH) have been installed"
fi
echo " * fabric is also installed"
echo " * and mercurial"
echo " * and ccgapps-settings"


# tell the (l)user how to activate this python install
echo -e "\n\nTo activate this python install, type the following at the prompt:\n\nsource $VPYTHON_DIR/bin/activate\n"
echo -e "To exit your virtual python, simply type 'deactivate' at the shell prompt\n\n"
