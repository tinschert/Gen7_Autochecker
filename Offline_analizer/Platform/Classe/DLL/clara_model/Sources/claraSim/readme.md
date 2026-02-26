# [claraSim](https://sourcecode01.de.bosch.com/projects/CLARAVR/repos/claravr_clarasim)

## Link to TDP (Tool Development Plan)

[TDP_CLARA](https://sourcecode01.de.bosch.com/projects/CLARAVR/repos/claravr_tools/browse/setup/clara/TDP_CLARA/TDP_CLARA.md?at=744a3c8ecc384065f26688710a9f25d11d2b7bf2)

## C++ simulation framework

### What does the submodule do?

This submodule provides the basic classes and methods to implement a simulation world. The easiest model
might be the road model that can be found in @roadNetwork. There a clothoid model for a road is implemented.
Additionally, a lane model is implemented, e.g. to implement a two-lane-road or a highway-road with many
lanes.
The most detailed model is the vehicle model, which should represent the ego vehicle where the device under
test (RADAR) is mounted. The vehicle model incorporates additional models like the drive train, the steering
system, etc. The underlying 2-lane vehicle model allows to perform driving maneuvers that are relevant
for intelligent cruise control (ACC), automated emergency braking (PSS) and other functions.
The submodule claraSim is used by every CLARA project and the simulation world is instantiated in the CSimWorld.cpp file.

### Why is the submodule useful?

This submodule contains the simulation world of CLARA. As mentioned in the CLARA wiki [Introduction](https://connect.bosch.com/wikis/home?lang=de-de#!/wiki/We36c98fbb784_4cd6_ae57_42b7f1464aa3/page/Introduction),
a simulation is necessary to create a closed-loop HiL. The simulation creates a virtual
world that the sensor cannot distinguish from the real world. Therefore, particular tests
 can be performed that require a feedback loop for the radar sensor. *IMPORTANT*: Simulations
require models. The models that are realized in this submodule can be found in the paragraphs below.

### How to get started?

* Make sure to understand CLARA and especially the [Introduction](https://connect.bosch.com/wikis/home?lang=de-de#!/wiki/We36c98fbb784_4cd6_ae57_42b7f1464aa3/page/Introduction) pages.
* Clone the [playground](https://sourcecode.socialcoding.bosch.com/projects/CLARA/repos/claravr_prj_playground_a1) project and make it run by creating a Linux application (see [help](https://connect.bosch.com/wikis/home?lang=de-de#!/wiki/We36c98fbb784_4cd6_ae57_42b7f1464aa3/page/New%20Project%20in%20claraVR)).
* The claraSim content is used by CLARA project automatically. Start playing with the "CSimModel.cpp" file in
the simulation-folder of the playground project. Consider changing the "p_xyzVehicleMountingPos" value.
  * Remake the project and observe that the radar position changed. At this point, the claraSim classes have not
been manipulated, because only an instance of the simulation world was manipulated by changing "CSimModel.cpp".
* The next step is to change the content in the claraSim files. Feel free to play with the multitudinous parameters,
change them, remake the project, and observe its effects on the simulation.

### How to contribute to the submodule?

1. Read the contributing guidelines [CONTRIBUTING.md](./CONTRIBUTING.md)
2. If you want to contribute to the claraSim submodule, first, it is advised to get a feeling for the submodule.
The [playground](https://sourcecode.socialcoding.bosch.com/projects/CLARA/repos/claravr_prj_playground_a1) project is a good start to get in touch with the submodule.
An alternative is to get involved in a customer project first, acquire some experience with CLARA and
contribute during the project. Of course, there are alternatives to get started.

### Need an idea :bulb: for contributions for the submodule? Here we go:

1. Documentation on everything you consider useful. Especially, documentation on exisiting code.
2. The speed controller is currently a PI-controller ([Wikipedia](https://en.wikipedia.org/wiki/PID_controller)). Feel free to implement new versions or maybe a Kalman-Filter.
3. Please feel free to introduce new features in the clara simulation world. Consider discussing your ideas in the [CLARA forum](https://connect.bosch.com/forums/html/forum?id=26df9506-6515-41b4-9fd6-b7def2bdbe03).
4. Documenting "Best practices": Consider writing a comment where you highlight how to use a test step, or method. E.g: How to instantiate "CWorld" (see CSimWorld.cpp in the playground for an example).


# claraSim doxygen

## Content and Attributes of claraSim:

* Windows and Linux (VC and GNU C++)
* Integration method
* Multiprocessing
* Lowpass filter, Table, Spline and Clothoid class
* Model based on simulation framework
* 2-lane vehicle model (horizontal and vertical dynamic)
* Power train and brake model
* Driver model
* Sensor model
*- Environment model
  * Road network
  * Dynamic objects
  * Static objects

For an overview of the simulation model, please open <a href="modules.html">Modules</a> tab in doxygen doc.

add this repository as submodule ***claraSim*** to your customer project

@defgroup framework framework
@defgroup world world
    @defgroup obstacle obstacle
    @ingroup world
    @defgroup roadNetwork roadNetwork
    @ingroup world
    @defgroup vehicle vehicle
    @ingroup world
        @defgroup chassis chassis
        @ingroup vehicle
        @defgroup dashboard dashboard
        @ingroup vehicle
        @defgroup driver driver
        @ingroup vehicle
        @defgroup driveTrain driveTrain
        @ingroup vehicle
        @defgroup sensor sensor
        @ingroup vehicle
        @defgroup steeringSystem steeringSystem
        @ingroup vehicle
