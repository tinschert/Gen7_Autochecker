Needed to build DLLs:
- Visual Studio 16 2019 (better 2022 version, which can fix some VCTargetsPath.vcxproj version v143 issue)
- python
- Conan (install via pip install https://docs.conan.io/2/installation.html)
- Add Conan to Path in System Environment Variables

Version 1.1
- 1objXloc model is now capable of generating the byte array for CAN TP and Ethernet. For the Conti usecase it is also implemented, but the final DataHandling is missing.
- 1objXloc model is now generating the radial distances of locations with a minimum of 0.1m due to testing in Ford has shown, that locations with distance = 0 are resulting in the Toliman PER breaking
- Statistical distribution model is enhanced by sending the edge points of the target as the first 3 locations and all locations coming after are distributed by the statistical model
- Added SNR and RSSI interfaces, both being put into the dll and later read from the dll without any calculations done inside the dll
- Updated maximum locations possible to 1056 and added radar specific handling of max locations (500 for CAN BUS/CAN TP, 1000 for Eth, 1056 for Conti)
- Fixed some issues on location generation in the near field

Version 1.0
- Implemented the RoadObj.dll containing the rotation of the given inputs, the object calculations for Video and SGU radars aswell as the 1objXloc model