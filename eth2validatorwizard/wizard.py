import sys

from eth2validatorwizard import __version__

from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import button_dialog

from eth2validatorwizard.platforms import (
    get_install_steps,
    supported_platform,
    has_su_perm,
    init_logging,
    quit_install,
    get_save_state,
    get_load_state
)

from eth2validatorwizard.platforms.common import StepSequence, is_completed_state

def run():
    # Main entry point for the wizard.

    platform = supported_platform()

    if not platform:
        # This is not a supported platform
        show_unsupported_platform()
        quit_install(platform)
    
    init_logging(platform)

    if not has_su_perm(platform):
        # User is not a super user
        show_not_su()
        quit_install(platform)
    
    if not show_welcome():
        # User asked to quit
        quit_install(platform)

    self_update()

    steps = get_install_steps(platform)
    if not steps:
        # Steps were not found for the current platform
        print('No steps found for current platform')
        quit_install(platform)
    
    save_state = get_save_state(platform)
    if not save_state:
        # save_state was not found for the current platform
        print('No save state found for current platform')
        quit_install(platform)
    
    sequence = StepSequence(steps=steps(), save_state=save_state)

    # Detect if installation is already started and resume if needed
    saved_state = get_load_state(platform)()
    if (
        saved_state is not None and
        'step' in saved_state and
        'context' in saved_state
        ):
        # We might be able to resume from an earlier execution
        if is_completed_state(saved_state):
            # TODO: Add features for when we already completed the wizard
            print('Wizard was already completed.')
            quit_install(platform)
        
        saved_step = sequence.get_step(saved_state['step'])
        if saved_step is not None:
            # Prompt the user to see if he wants to resume from saved_step
            resume_result = prompt_resume(saved_step)
            if not resume_result:
                # User asked to quit
                quit_install(platform)
            elif resume_result == 1:
                return sequence.run_from_step(saved_step.step_id, saved_state['context'])

    # Start a brand new installation
    if not explain_overview():
        # User asked to quit
        quit_install(platform)

    # Execute the platform dependent steps from the start
    return sequence.run_from_start()

def show_welcome():
    # Show a welcome message about this wizard

    result = button_dialog(
        title='Eth2 Validator Wizard',
        text=(
'''
Welcome to the Eth2 Validator Wizard!

This setup assistant is meant to guide anyone through the different steps
to become a fully functional validator on the Ethereum 2.0 network. It will
install and configure all the software needed to become a validator.

If you have any question or if you need additional support, make sure
to get in touch with the ethstaker community on:

* Discord: discord.gg/e84CFep
* Reddit: reddit.com/r/ethstaker
'''     ),
        buttons=[
            ('Start', True),
            ('Quit', False)
        ]
    ).run()

    return result

def prompt_resume(step):
    # Show prompt for user to resume from a previous step

    result = button_dialog(
        title='Previous installation found',
        text=(HTML(
f'''
It seems like you already started the wizard previously.

You were at following step: <b>{step.display_name}</b>

Would you like to resume at this step or restart the full setup from the
beginning?
'''     )),
        buttons=[
            ('Resume', 1),
            ('Restart', 2),
            ('Quit', False),
        ]
    ).run()

    return result

def self_update():
    # TODO: Check for a new version of the wizard and self-update if needed

    pass

def show_not_su():
    # Show a message about the wizard not having super user (root or sudo) permissions

    button_dialog(
        title='Not a super user',
        text=(
'''
The Eth2 Validator Wizard needs to have super user permissions in order
to proceed.

A simple way to give the wizard these permissions is to start it with sudo.
'''     ),
        buttons=[
            ('Quit', False)
        ]
    ).run()

def explain_overview():
    # Explain the overall process of becoming a validator

    result = button_dialog(
        title='Becoming a validator',
        text=(
'''
Here is an overview of the different steps required to become an active
validator on an Ethereum 2.0 network.

* Consolidate 32 ETH for each active validator you want (You can have
a large amount of active validators using a single machine and this setup)
* Install an Eth1 client and let it synchronize
* Generate your validator(s) keys
* Install an Eth2 beacon node and let it synchronize
* Install an Eth2 validator client and import your key(s)
* Perform the 32 ETH deposit for each validator
* Wait for your validator(s) to become active (can take a few hours/days)
'''     ),
        buttons=[
            ('Keep going', True),
            ('Quit', False)
        ]
    ).run()

    return result

def show_unsupported_platform():
    # Show a message about the current platform not being supported

    button_dialog(
        title='Platform not supported',
        text=(HTML(
'''
The Eth2 Validator Wizard has no support for your platform. We only support
the following platforms:

* <b>Ubuntu 20.04</b> (x86_64)
* <b>Windows 10</b> (amd64)
'''     )),
        buttons=[
            ('Quit', False)
        ]
    ).run()