*** Keywords ***
Print
   say_hello_world

PrintMessage
    [Arguments]     ${text}
    output_message  ${text}

Отпечатай Съобщение
    [Arguments]     ${text}
    output_message  ${text}

Set CANoe Bus Signal
    [Arguments]             ${namespace}     ${name}        ${value}
    Write_CANoe_Symbol      ${namespace}     ${name}        ${value}

Set CANoe System Variable
    [Arguments]             ${namespace}     ${name}        ${value}
    Write_CANoe_Symbol      ${namespace}     ${name}        ${value}

Start HTML logging
    [Arguments]         ${string1}     ${string2}        ${filename}
    HTML_Logger.setup   ${string1}     ${string2}        ${filename}

Стартирай логване в HTML формат
    [Arguments]         ${string1}     ${string2}        ${filename}
    HTML_Logger.setup   ${string1}     ${string2}        ${filename}

Чакай Докато
    [Arguments]          ${namespace}     ${name}        ${exp_value}        ${timeout}
    Await_Value_Match    ${namespace}     ${name}        ${exp_value}        ${timeout}

Отвори връзка през XIL API с CANoe
    Open_Connection

Сетни променлива на CANoe
    [Arguments]             ${namespace}     ${name}        ${value}
    SetSignal               ${namespace}     ${name}        ${value}

Сетни променлива тип масив на CANoe
    [Arguments]             ${namespace}     ${name}        ${value}
    SetSignal_Array         ${namespace}     ${name}        ${value}

Изчакай определено време
    [Arguments]             ${time_ms}
    TestWaitForTimeout      ${time_ms}

Ускори ego-то до зададена скорост
    [Arguments]                  ${speed}
    Set_Ego_Vehicle_Velocity     ${speed}

Провери сигнал
    [Arguments]          ${namespace}     ${name}        ${exp_value}
    CheckSignal          ${namespace}     ${name}        ${exp_value}