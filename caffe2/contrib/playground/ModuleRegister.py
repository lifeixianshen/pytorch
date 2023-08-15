from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import inspect
import logging
logging.basicConfig()
log = logging.getLogger("ModuleRegister")
log.setLevel(logging.DEBUG)

MODULE_MAPS = []


def registerModuleMap(module_map):
    MODULE_MAPS.append(module_map)
    log.info(
        f"ModuleRegister get modules from  ModuleMap content: {inspect.getsource(module_map)}"
    )


def constructTrainerClass(myTrainerClass, opts):

    log.info(f"ModuleRegister, myTrainerClass name is {myTrainerClass.__name__}")
    log.info(f"ModuleRegister, myTrainerClass type is {type(myTrainerClass)}")
    log.info(f"ModuleRegister, myTrainerClass dir is {dir(myTrainerClass)}")

    myInitializeModelModule = getModule(opts['model']['model_name_py'])
    log.info(
        f"ModuleRegister, myInitializeModelModule dir is {dir(myInitializeModelModule)}"
    )

    myTrainerClass.init_model = myInitializeModelModule.init_model
    myTrainerClass.run_training_net = myInitializeModelModule.run_training_net
    myTrainerClass.fun_per_iter_b4RunNet = \
        myInitializeModelModule.fun_per_iter_b4RunNet
    myTrainerClass.fun_per_epoch_b4RunNet = \
        myInitializeModelModule.fun_per_epoch_b4RunNet

    myInputModule = getModule(opts['input']['input_name_py'])
    log.info(
        f"ModuleRegister, myInputModule {opts['input']['input_name_py']} dir is {myInputModule.__name__}"
    )

    # Override input methods of the myTrainerClass class
    myTrainerClass.get_input_dataset = myInputModule.get_input_dataset
    myTrainerClass.get_model_input_fun = myInputModule.get_model_input_fun
    myTrainerClass.gen_input_builder_fun = myInputModule.gen_input_builder_fun

    # myForwardPassModule = GetForwardPassModule(opts)
    myForwardPassModule = getModule(opts['model']['forward_pass_py'])
    myTrainerClass.gen_forward_pass_builder_fun = \
        myForwardPassModule.gen_forward_pass_builder_fun

    myParamUpdateModule = getModule(opts['model']['parameter_update_py'])
    myTrainerClass.gen_param_update_builder_fun =\
        myParamUpdateModule.gen_param_update_builder_fun \
        if myParamUpdateModule is not None else None

    myOptimizerModule = getModule(opts['model']['optimizer_py'])
    myTrainerClass.gen_optimizer_fun = \
        myOptimizerModule.gen_optimizer_fun \
        if myOptimizerModule is not None else None

    myRendezvousModule = getModule(opts['model']['rendezvous_py'])
    myTrainerClass.gen_rendezvous_ctx = \
        myRendezvousModule.gen_rendezvous_ctx \
        if myRendezvousModule is not None else None

    # override output module
    myOutputModule = getModule(opts['output']['gen_output_py'])

    log.info(f"ModuleRegister, myOutputModule is {myOutputModule.__name__}")
    myTrainerClass.fun_conclude_operator = myOutputModule.fun_conclude_operator
    myTrainerClass.assembleAllOutputs = myOutputModule.assembleAllOutputs

    return myTrainerClass


def overrideAdditionalMethods(myTrainerClass, opts):
    log.info(
        f"B4 additional override myTrainerClass source {inspect.getsource(myTrainerClass)}"
    )
    # override any additional modules
    myAdditionalOverride = getModule(opts['model']['additional_override_py'])
    if myAdditionalOverride is not None:
        for funcName, funcValue in inspect.getmembers(myAdditionalOverride,
                                                      inspect.isfunction):
            setattr(myTrainerClass, funcName, funcValue)
    log.info(
        f"Aft additional override myTrainerClass's source {inspect.getsource(myTrainerClass)}"
    )
    return myTrainerClass


def getModule(moduleName):
    log.info(
        f"get module {moduleName} from MODULE_MAPS content {str(MODULE_MAPS)}"
    )
    myModule = None
    for ModuleMap in MODULE_MAPS:
        log.info(f"iterate through MODULE_MAPS content {str(ModuleMap)}")
        for name, obj in inspect.getmembers(ModuleMap):
            log.info(f"iterate through MODULE_MAPS a name {str(name)}")
            if name == moduleName:
                log.info(
                    f"AnyExp get module {moduleName} with source:{inspect.getsource(obj)}"
                )
                return obj
    return None


def getClassFromModule(moduleName, className):
    myClass = None
    for ModuleMap in MODULE_MAPS:
        for name, obj in inspect.getmembers(ModuleMap):
            if name == moduleName:
                log.info(
                    f"ModuleRegistry from module {moduleName} get class {className} of source:{inspect.getsource(obj)}"
                )
                return getattr(obj, className)
    return None
