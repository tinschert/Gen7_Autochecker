using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FlashingLib
{
    /**
     * @copyright  (C) 2019-2020 Robert Bosch GmbH.\n
     * The reproduction, distribution and utilization of this file as well as
     * the communication of its contents to others without express authorization
     * is prohibited.\n
     * Offenders will be held liable for the payment of damages.\n
     * All rights reserved in the event of the grant of a patent, utility model or design.
     *
     * @file         Logging.cs
     *
     * @brief Class for logging.
     * @details Class for logging. Any console printing, log generation shall be handled here.\n
     */
    public class Logging
    {

        //! application method that logs Info
        static public Action<string> infoLoggerMethod = null;

        //! application method that logs Pass
        static public Action<string> passLoggerMethod = null;

        //! application method that logs Fail
        static public Action<string> failLoggerMethod = null;

        //! application method that logs Error
        static Action<string> errorLoggerMethod = null;

        public enum ReturnCodes {
            Pass = 1,
            Fail = 2,
            Error = 3
        }

        /**
        * Through this method an application method can be registered to be called to be called with info logging.
        *
        * @param[in]	 failLoggerMethod Name of the logger method
        */
        public static void registerInfoLoggingFunction(Action<string> infoLoggerMethod) {
            Logging.passLoggerMethod = infoLoggerMethod;
        }

        /**
        * Through this method an application method can be registered to be called to be called with pass logging.
        *
        * @param[in]	 failLoggerMethod Name of the logger method
        */
        public static void registerPassLoggingFunction(Action<string> passLoggerMethod)
        {
            Logging.passLoggerMethod = passLoggerMethod;
        }

        /**
        * Through this method an application method can be registered to be called to be called with fail logging.
        *
        * @param[in]	 failLoggerMethod Name of the logger method
        */
        public static void registerFailLoggingFunction(Action<string> failLoggerMethod)
        {
            Logging.failLoggerMethod = failLoggerMethod;
        }

        /**
        * Through this method an application method can be registered to be called to be called with error logging.
        *
        * @param[in]	 errorLoggerMethod Name of the logger method
        */
        public static void registerErrorLoggingFunction(Action<string> errorLoggerMethod)
        {
            Logging.errorLoggerMethod = errorLoggerMethod;
        }

        /**
        * Reports info to the console
        *
        * @param[in]	 methodName Name of the logger method
        * @param[in]	 v String to print.
        */
        public static void printInfo(string methodName, string v)
        {
            if (Logging.infoLoggerMethod != null)
            {
                Logging.infoLoggerMethod("Info | Method(" + methodName + "): " + v);
            }
            Console.WriteLine("Info | Method(" + methodName + "): " + v);
        }

        /**
        * Reports a successful step to the console
        *
        * @param[in]	 methodName Name of the logger method
        * @param[in]	 v String to print.
        */
        public static void printPass(string methodName, string v)
        {
            if (Logging.passLoggerMethod != null) {
                Logging.passLoggerMethod("Pass | Method(" + methodName + "): " + v);
            }
            Console.WriteLine("Pass | Method(" + methodName + "): " + v);
        }

        /**
        * Reports a Failed step to the console
        *
        * @param[in]	 methodName Name of the logger method
        * @param[in]	 v String to print.
        */
        public static void printFail(string methodName, string v)
        {
            if (Logging.failLoggerMethod != null)
            {
                Logging.failLoggerMethod("Fail | Method(" + methodName + "): " + v);
            }
            Console.Error.WriteLine("Fail | Method(" + methodName + "): " + v);
        }

        /**
        * Reports an Error to the console
        *
        * @param[in]	 methodName Name of the logger method
        * @param[in]	 v String to print.
        */
        public static void printError(string methodName, string v)
        {
            if (Logging.errorLoggerMethod != null)
            {
                Logging.errorLoggerMethod("Error | Method(" + methodName + "): " + v);
            }
            Console.Error.WriteLine("Error | Method(" + methodName + "): " + v);
        }

    }
}
