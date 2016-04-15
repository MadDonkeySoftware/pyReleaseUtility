(function(release_util, $) {
    //Private Property
    var URL_SEP = '/';

    //Private Method
    function demo(arg){
    }

    //Public Property
    release_util.logging = {};

    //Public Method
    release_util.logging.debug = function(message){
        if (window.console){
            window.console.log(message);
        }
    };

    release_util.logging.warn = function(message){
        if (window.console){
            window.console.warn(message);
        }
    };

    release_util.logging.error = function(message){
        if (window.console){
            window.console.error(message);
        }
    };

    release_util.stringHelpers = {};
    release_util.stringHelpers.capitalizeFirstLetter = function(str){
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
}( window.release_util = window.release_util || {}, jQuery ));
