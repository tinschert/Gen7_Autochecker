
# TDP ADAS HIL - Advanced Driver Assist System Hardware in the Loop

> © This document is the exclusive property of Robert Bosch GmbH. Without their
consent it may not be reproduced or given to third parties. If printed, this is
an uncontrolled document. The user must verify it is an authorized edition prior
to use.

*Template for the Tool Development Plan - Processes, Regulations and execution
guidelines for tool development in XC-DX*

*If you identify an opportunity to improve this process, complete CC-DD0206-1s1
and submit to XC-DX/EPG.*

For details on purpose, scope, definition of terms, additional information and
good practices refer to the [appendix](#appendix) or [TDP template](https://abt-prolib.de.bosch.com/stages/#/workspace/203/_vv/(process/activity/_x0d7gBlg2WOSXYKrW5pqsg//dialog:process/description/_TuCSgHFb9TGSXYKrW5pqsg/targetWorkspaceId/203))
in DA Processes.

# 1. Tool information

| Tool identification        |                                              |
| -------------------------- | -------------------------------------------- |
| Tool name                  | ADAS HIL - Advanced Driver Assist System Hardware in the Loop                                    |
| Tool description (short)   | Hardware in the Loop environment for ADAS ECU or MultiECU systems                               |


## 1.1. Tool project organization

In every tool development project, the roles defined shall be mentioned explicitly.

| Domain     | Tool roles    | Designation       | Tasks, responsibilities  |
| ---------- | ------------- | ----------------- | ------------------------ |
| Tool project | Tool responsible      | Rafael Herrera XC-AS/EDI2 | Ref. process landscape role description: [Tool responsible](http://abt-prolib.de.bosch.com:8080/pkit/go/process/element.do?elementType=Role&elementName=Generic+Roles%7CTool+Responsible&projectName=proCCess+library%7CDAS)   |
|              | Tool owner            | XC-AS/EDI | Ref. process landscape role description: [Tool owner](http://abt-prolib.de.bosch.com:8080/pkit/go/process/element.do?elementType=Role&elementName=Generic+Roles%7CTool+Owner&projectName=proCCess+library%7CDAS)   |
|              | Sponsor               | Hans-Christian Swoboda XC-AS/EDI | Ref. process landscape role description: [Sponsor](http://abt-prolib.de.bosch.com:8080/pkit/go/process/element.do?elementType=Role&elementName=Organizational+Roles%7CSponsor&projectName=proCCess+library%7CDAS) |
| Central      | Process responsible   | Ref. process landscape [role designation](https://inside-ilm.bosch.com/irj/go/nui/sid/download/blatestvalidversion/70c1824f-1ea2-3110-6a80-a53c75c9a665) | Ref. process landscape role description: [Process responsible](http://abt-prolib.de.bosch.com:8080/pkit/go/process/element.do?elementType=Role&elementName=Organizational+Roles%7CPR%3A+Process+Responsible&projectName=proCCess+library%7CDAS)  |
|              | Process expert        | Ref. process landscape [role designation](https://inside-ilm.bosch.com/irj/go/nui/sid/download/blatestvalidversion/70c1824f-1ea2-3110-6a80-a53c75c9a665) | Ref. process landscape role description: [Process expert](http://abt-prolib.de.bosch.com:8080/pkit/go/process/element.do?elementType=Role&elementName=Organizational+Roles%7CPE%3A+Process+Expert&projectName=proCCess+library%7CDAS)  |
|              | Tool CCB              | Ref. process experts  | Ref. process landscape role description: [Tool CCB](http://abt-prolib.de.bosch.com:8080/pkit/go/process/element.do?elementType=Role&elementName=Organizational+Roles%7CTool+CCB%3A+Tool+Change+Control+Board&projectName=proCCess+library%7CDAS)      |


## 1.2. Tool documentation

The description and documentation of the tool shall be provided here or via link
to external reference: 
[Bosch Tube](https://tube.video.bosch.com/channel/ADAS%2BXIL/4470)
[Wikipedia](https://inside-docupedia.bosch.com/confluence/display/ADASXIL/04+ADAS+HIL)
[BOM Bill of Material](https://sourcecode01.de.bosch.com/projects/PJXIL/repos/adas_hil/browse/Release/SW_BoM_ADAS_HIL_PF.yml)

## 1.3. Decision on tool development

*For new tools and for future decisions on major tool updates where a decision is*
*required the following information shall be provided.*
*If tool and corresponding TDP already exists (e.g. update of TDP to current*
*template) this information can be provided optionally.*

A specification of the predicted initial development effort and the annual
maintenance effort for the planned tool activity shall be provided
that includes internal personal effort as well as external costs.

If applicable, existing alternative tools shall be evaluated and the benefit of
the planned tool shall be documented in comparison to these.

Is tool development approved? **YES**

If applicable, document relevant information from decision or reasoning here.

## 1.4 Relevance assessment

| Section | Domain                     | Relevance      | Criteria                                                                                   |
| ------- | -------------------------- | -------------- | ------------------------------------------------------------------------------------------ |
| 1.4.1   | OSS (Open Source Software) | **{{NO}}** | The tool contains OSS or introduces OSS parts into the product                             |
| 1.4.2   | Third party software       | **{{NO}}** | The tool contains third party software or introduces  third party parts into the product   |
| 1.4.3   | Security                   | **{{NO}}** | The tool uses, configures or processes cryptographic primitives or security configurations. <br> The tool creates product source code or executables |
| 1.4.4   | Data protection            | **{{NO}}** | Person related data is collected, stored or processed by the tool                          |

For all relevant domains ensure that the below listed measure and tasks are fulfilled
and the corresponding documentation is available.

### 1.4.1 OSS - Measure and tasks

A documentation of the OSS parts (packages or snippets) contained in the tool
and a documentation if the tool introduces OSS parts into the product shall be
provided here or via link to external reference:
[OSS analysis]
The code is based on capl code inbuilt in CANoe tool and libraries where a license is needed to be run. The code is either manually generated (using in built CANoe libraries) or autogenerated by python scripts.
The scripts contained in folder Platform/Classe/Scripts are developed in-house by Robert Bosch Gmbh using python open source libraries:
The scripts use open source libraries all rights reserved to the respective library developers. The list of libraries can be found in the \Release\SW_BoM_ADAS_HIL_PF.yml

### 1.4.2 3rd party SW - Measure and tasks

Not applicable

### 1.4.3 Security - Measure and tasks

Not applicable

### 1.4.4 Data protection relevance

Is person related data collected, stored or processed by the tool? **NO**

# 2. Classification

In general, the maximum ASIL for safety requirements that can be violated by the
software tool is considered as ASIL D. The classification is done for each use case.

The context of the classification is the DAS (XC-AS/XC-AC) process landscape.

If the classification is documented outside of the TDP (e.g. ClassiQ Windows client)
the link to classification report shall be documented here:
[External tool classification documentation](https://sites.inside-share2.bosch.com/sites/104307/default.aspx?RootFolder=%2Fsites%2F104307%2FDocuments%2FTDP%2FTDP%5FCLASSE&FolderCTID=0x0120008F0E9138E1352A49BB16731B2B7476EF&View=%7B52E4FF42%2DDB16%2D46E3%2DB34B%2DB36FB888FF50%7D).


## 2.1.	Classification summary

| S. No     | Use Case            | Feature           | Determined TCL Value   | 
| --------- | ------------------- | ----------------- | ---------------------- |
| 1         | Hardware blue print |  see [Qualification and Classification revision 2.5](https://inside-share-hosted-apps.bosch.com/DMS/GetDocumentService/Document.svc/GetDocumentURL?documentID=P12S104307-561675005-2031)      | TCL2 |
| 2         | System Integration - Network test |  see [Qualification and Classification revision 2.5](https://inside-share-hosted-apps.bosch.com/DMS/GetDocumentService/Document.svc/GetDocumentURL?documentID=P12S104307-561675005-2031)      | TCL2 |
| 3         | System Integration - MultiECU test |  see [Qualification and Classification revision 2.5](https://inside-share-hosted-apps.bosch.com/DMS/GetDocumentService/Document.svc/GetDocumentURL?documentID=P12S104307-561675005-2031)      | TCL2 |
| 4         | System Test - Application Software test |  see [Qualification and Classification revision 2.5](https://inside-share-hosted-apps.bosch.com/DMS/GetDocumentService/Document.svc/GetDocumentURL?documentID=P12S104307-561675005-2031)      | TCL2 |


Required TCL value for the tool is: **TCL2**

Determine the TCL based the following table:

| Tool impact | Tool error detection |   |   |
| ----------- | ------- | ------- | -------- |
|             | **TD1** | **TD2** | **TD3**  |
| **TI1**     | TCL1    | TCL1    | TCL1     |
| **TI2**     | TCL1    | TCL2    | TCL3     |



# 3. Tool development activities

The development proceeds according to the V-model or other suitable standard
software development models. It shall prevent errors in the developed item and
create traceability throughout the development artefact (requirements –
implementation – testing - release).

This chapter describes and documents the applied development activities.


## 3.1. Schedule

A milestone plan shall be created for a tool project. The milestone plan for
tool projects with “indefinite” project run time must be updated at least once
a year.

[Roadmap - tool project schedule](https://rb-tracker.bosch.com/tracker08/secure/PortfolioPlanView.jspa?id=13872&sid=14234&vid=18851#plan/backlog).


## 3.2. Requirements management

A tool project shall provide the definition and documentation of
requirements/objectives with the sponsor before the execution phase. Major
changes during the course of the tool project have to be documented.

ADAS HIL is intended for SYS_INT, SW_INT and SYS_TST for BSW and ASW domain. Use cases:
* Gateway simulation for car configuration on multiple ECUs and their multiple variants.
* Flashing and diagnostic trouble code analysis. 
* Interface verification cross component
* Degradation Tests on reduced sensor sets and cross component degradation 
* Synchronized Power up and shut down  for network management
* Time synchronization of the ECUs with Global Common Time 
* Replay of a Vehicle Trace for field returns analysis and integration problem solving 
* MultiECU system integration
* Network tests in closed loop
* ADAS Longitudinal and Lateral functional testing
* Perception and Situation testing

[Requirements management](https://inside-docupedia.bosch.com/confluence/display/ADASXIL/01_Requirements?src=contextnavpagetreemode)

## 3.3. Change request/Problem resolution management

Tool project shall document how changes can be requested, how defects
can be reported and how they are managed subsequently (e.g. T&R).

Changes, fixes and modifications shall be requested over T&R tickets. The ticket shall be issued in the following form:

* *Item: Story
* *Summary: prefix [ADAS_HIL] then write a short title of the request
* *Assignee: Tool responsible (refer to TDP for current responsibility matrix)
* *Description: please add the affected release, tested vehicle variant, software release and calibration and a full bus trace (blf format) as well as any other useful data like canapé mf4 traces.
* *Team: ADAS_XIL_WS3

Link to [T&R Board](https://rb-tracker.bosch.com/tracker08/secure/RapidBoard.jspa?rapidView=89253).

[Change request workflow](https://inside-docupedia.bosch.com/confluence/display/ADASXIL/a_Configuration+management)

## 3.4. Configuration management

Configuration management in the tool project addresses two aspects:

1. Versioning of SW and HW artifacts shall be carried out in a tool project.
Related documents of a tool project must be stored uniformly in a central tools
directory.
2. It is recommended that the developed tool provides measures to support
projects in configuration management. (E.g. by providing a tool ID, tool
configuration, … with each created artefact to facilitate traceability and allow reproduction of results).


### 3.4.1. CM in tool development

SW and tool project artifacts shall be under version control (e.g. MKS, GIT, …):

[Tool version control and storage location ADAS HIL (CANoe repo)](https://sourcecode01.de.bosch.com/projects/PJXIL/repos/adas_hil/browse).

[Tool version control and storage location Platform (Common code repo)](https://sourcecode01.de.bosch.com/projects/PJXIL/repos/platform/browse).

[Tool version control and storage location ADAS Sim (Carmaker repo)](https://sourcecode01.de.bosch.com/projects/PJXIL/repos/adas_sim/browse).

The folder structure in the tool project shall be documented: [Documentation](https://inside-docupedia.bosch.com/confluence/display/ADASXIL/a_Configuration+management). 

[Git repository handling](https://inside-docupedia.bosch.com/confluence/display/ADASXIL/a_Configuration+management).

[Integration guidelines for customer projects](https://inside-docupedia.bosch.com/confluence/display/ADASXIL/a_Configuration+management) 

### 3.4.2. CM in tool operation

Testing services, libraries, automation (CI/CT) is compatible with the FAST tool.
[Reference to FAST tool TDP](https://sites.inside-share3.bosch.com/sites/104307/default.aspx?RootFolder=%2Fsites%2F104307%2FDocuments%2FTDP%2FTDP%5FFAST&FolderCTID=0x0120008F0E9138E1352A49BB16731B2B7476EF&View=%7B52E4FF42%2DDB16%2D46E3%2DB34B%2DB36FB888FF50%7D)


## 3.5. Quality assurance

Quality assurance measures shall be implemented and documented in the tool project.

The individual measures shall be described and documented.

(Add additional and remove not applied measures from table or provide on an
alternative documentation).

| Quality assurance measure   | Description    | When        | Status       |
| --------------------------- | -------------- | ----------  | ------------ |
| Evaluation of the tool development process  | See ISO 26262-8 11.4.8  | TDP Release  | Completion status of tool development process | 
| Validation of the software tool   | A set of tests according to the validation concept specified [Validation Concept](https://inside-share-hosted-apps.bosch.com/DMS/GetDocumentService/Document.svc/GetDocumentURL?documentID=P12S104307-561675005-2031) are conducted  | Each Tool release   | Ref. [README.md](https://sourcecode01.de.bosch.com/projects/PJXIL/repos/adas_hil/browse)  |


## 3.6. Tool acceptance, release and archiving

The procedure for tool release shall be described and documented.

A release is defined by a new version of the source code repository.
The release is documented in the file [README.md](https://sourcecode01.de.bosch.com/projects/PJXIL/repos/platform/browse/README.md) of the Release folder in the Platform repository.

Important: a release in a customer project is only complete when the customer project tests mentioned in the validation concept are developed and fulfilled in the customer project release documentation.

Please refer to the branches naming based explained in the chapter configuration management above.

The creation of a new branch in origin it is an official release.

A release must at least contain:

* Documentation of taken quality assurance measures
* Documentation of quality status of the measures
* Documentation of deviations from tool quality assurance plan, if applicable
* Documentation usage constraints, malfunctions  and limitation of the tool
* Documentation of the valid TDP version (including valid TDP artifacts) for
each release in case multiple TDP versions exist
* Documentation of dependencies for tool operation (e.g. specific version of operation systems, COTS, …), if applicable
* Documentation of [SW consulting service](https://www.intranet.bosch.com/app/swc/webrequest/frm_SoftwareRequest.aspx)
for used SW (COTS, Freeware, OSS, …), if applicable

Long term storage archiving applies for the ADAS HIL tool. This means that it applies for every customer project usign the ADAS HIL. The storage of the tool versions and installers should be kept for 35 years as well as the hardware.
[LTM Guidelines](https://inside-docupedia.bosch.com/confluence/display/XCLTM)

# 4. Release of TDP

A peer-review shall be performed for major changes of the TDP. The initial
release and changes in chapters Classification, Product acceptance, release,
archiving or quality assurance are considered as major changes. The
tool owner shall confirm all major changes. The sponsor shall confirm at least
the initial release.
Confirmation shall be conducted via WorkON workflow that a peer review has been
carried out and the following criteria are fulfilled:

* Tool development is in compliance with tool development process
* The latest template has been used
* The implemented processes are suitable for this tool project
* The use cases are complete and represent the intended use
* The reasoning of the TI and TD classification is valid
* The argued malfunction prevention/detection measures are in place and applied
in daily business
* The classification is free from assumptions, wishes, exceptions, conditions,
open issues
* The potential malfunctions are complete
* The quality assurance is suitable to reduce the risk of malfunction of TCL2/3
classified use cases.
* The tool can be used efficiently in projects

Minor changes can be released by the tool responsible.

The TDP comes into effect when published in the [TDP storage location](https://inside-share-hosted-apps.bosch.com/DMS/GetDocumentService/Document.svc/GetDocumentURL?documentID=P12S104307-561675005-29)
and the request for [release workflow](https://connect.bosch.com/forums/html/threadTopic?id=2e1815b8-7e01-4ba4-8335-c8fe967dabcc)
is successful finished.


# 5. Change history / change journal


## 5.1. Document

| Vers.No. | Date            | Author                     | Change           |
| -------- | --------------- | -------------------------- | ---------------- |
|          |                 |                            |                  |
|          |                 |                            |                  |

*Note: Document history can be maintained in any configuration management tool*
*(Eg.: SharePoint, BitBucket), document the configuration tool details here and*
*delete above table.*


## 5.2. Template

| Vers.No. | Date       | Author                        | Change  |               |                             |
| -------- | ---------- | ----------------------------- | ------- | ------------- | --------------------------- |
|          |            |                               | Chapter | Key word      | Brief description of change |
| 0.1      | 04.04.2016 | Ackermann Roland (CC-DA/EYD5) | all     | First version | Template                    |
| 0.2      | 27.04.2016 | Ebel Susanne, Erhart Robert   | 4       | Title changed | Use case Impact  / Use case error detection - title changed |
| 1.0      | 31.07.2019 | Schmidt Oliver (CC-AD/EYR1)   | all     | New Version   | Use case Impact  / Completely reworked all chapters in the template |
| 1.1      | 18.11.2019 | Schmidt Oliver (CC-AD/EYR1)   | 7 and 8 | Updated       | Section 7: Updated tool responsible link in Word Template and section 8: Replace Group Manager with Tool Owner |
| 1.2      | 22.11.2019 | Schmidt Oliver (CC-AD/EYR1)   | 7       | Updated       | Replaced ilm link with sharepoint link |
| 1.3      | 12.04.2019 | Jeeshma PR (RBEI/ESM5)        | 9       | Updated       | Updated history section |
| 1.4      | 17.01.2020 | Jeeshma PR (RBEI/ESM5)        | 7       | Updated       | Updated broken links for roles |
| 1.5      | 20.07.2020 | Schmidt Oliver (CC-AD/EYR1)   | all     | Updated       | Introduction of appendix to separate required input from additional information. Adaption due to introduction of new Tool Management Process (MAN_PTM) |
| 1.6      | 20.11.2020 | Schmidt Oliver (CC-AD/EYR1)   | all     | Updated       | Updated typo errors |
| 1.7      | 22.02.2021 | Karangadan Reshma (RBEI/EQM1-VS2), Schmidt Oliver (XC-AD/EYR1)   | all     | Updated       | Alignment with updated classification template from BBM CoC - N102 FS004; Editorial Changes due to adaption to XC Organisation; Copyright statement included |
| 1.8      | 08.07.2021 | Karangadan Reshma (RBEI/EQM1-VS2), Schmidt Oliver (XC-AD/EYR1)   | A3     | Updated       | Detailing definition for tool and use case. Corrected typos |
| 1.9      | 05.11.2021 | Karangadan Reshma (RBEI/EQM1-VS2), Schmidt Oliver (XC-AD/EYR1)   | 1.4.2, 3.3, A7     | Updated       | Introduction of requirements from SW license management. Introduction of problem resolution management. Update of OSS aspects.|
| 1.10      | 28.02.2022 | Karangadan Reshma (RBEI/EQM1-VS2), Schmidt Oliver (XC-AD/EYR1)   | 12, A2, A12     | Updated       | Changed organization name from DA to DX and removed XC-AD organization from process/template scope|
| 1.11      | 24.06.2022 | Karangadan Reshma (RBEI/EQM1-VS2), Schmidt Oliver (XC-AD/EYR1)   | 1.1     | Updated       | Fixed broken links due to stages 7 migration|
| 1.12      | 18.07.2022 | Erhart Robert (XC-DX/ETV1)   | HEADER    | Updated       | Fixed broken links due to stages 7 migration|
| 1.13      | 26.06.2022 | Schmidt Oliver (CC-AD/EYR1)   | 3.5,3.6   | Updated       | Added additional recommended Quality assurance measures, detailed the release steps.|
| 1.14      | 03.03.2023 | Karangadan Reshma (BGSW/EQM-XC-DA2)  | A2,A3    | Updated       | Added "Method - Open Software Guideline" into section A6 Additional information, and replaced CC-DD0301-2 with MP-201.1 XC Manage Product Development Projects.|
| 1.15      | 15.11.2023 | Schmidt Oliver (CC-AD/EYR1), Erhart Robert (XC-DX/ETV1)   | 1.4,3.5   | Updated       | added security needs and measures aligned with XC-ProVIRT, Summarized relevance assessments in one table, introduced TBOM (Tool Bill Of Material).|



# Appendix

This appendix contains additional information and good practices for selected
sections of the TDP that might help or support the completion of the TDP. This
appendix can be deleted if not needed.


## A1 Purpose

The aim of the tool development process and associated tool development plan
(TDP) is to provide a tool life cycle to ensure the required confidence in tools
to not introduce or fail to detect any safety or release relevant fault into the
product when using the tools. This process contributes that the state of the art
for the product is achieved. It implements the requirements for tools from
[ISO 26262-8](https://rb-normen.bosch.com/NormMaster/DirectLink.do?ACTION=VIEW_STANDARD&doknr=ISO+26262-8),
[CD00214](https://rb-wam.bosch.com/socos-c/SOCOS/finder.cgi?CD-00214-000_XXX_X_EN)
and [CDQ0302](https://rb-wam.bosch.com/socos-c/SOCOS/finder.cgi?CD-00302-000_XXX_X_XX).
As well this process ensures an efficient and timely tool development.

The Tool Development Plan can be considered as the Project Management Plan for
the tool development. As such it contains the core information about the tool
(responsibilities, classification, ...) and documents the planned development
activities for the tool including the references to the specific artifacts.

*Recommendation: A tool implementation independent TDP should be favored. In*
*such cases an update of the TDP is not required with a new tool version. But*
*of course, the development artifacts (QA measures, release note, ...) shall be*
*provided with each tool release.*


## A2 Scope

This process regulates the life cycle for tools in XC-DX. It includes
the creation, modification and configuration of tools and the use cases of
tools. These activities are considered within the TDP as tool development. Tool
development in XC-DX takes place only in the frame of projects,
mandated by projects or in responsible line organizations. In all cases these
development guidelines shall be used. If tool development takes place in
projects according to [MP-201.01 XC Manage Product Development Projects](https://abt-prolib.de.bosch.com/stages/#/workspace/203/_vv/process/guidance/_OCMfQMsKEu-7DN4Sc9b6jQ)
which are explicitly dedicated to the development of the tool (tool is delivery
item) additional requirements for the development process might result from
project management. The documentation of the process steps in the TPD is
recommended in such cases.

The usage of a out of context developed and qualified tool as it is, is not in
the scope of this process (e.g. XC-DX external tool, tool and use
case from different project, ...). Nevertheless, the TDP can be used also in such
cases to manage the tool life cycle and to confirm the validity of the use
cases and Validity of predetermined tool confidence level or qualification
([ISO 26262-8 11.4.2](https://rb-normen.bosch.com/NormMaster/DirectLink.do?ACTION=VIEW_STANDARD&doknr=ISO+26262-8)).

*Note: It is always in the responsibility of the tool user to confirm that the*
*content of the TDP complies with the intended usage of the tool.*

*Note: The [ISO 26262-8](https://rb-normen.bosch.com/NormMaster/DirectLink.do?ACTION=VIEW_STANDARD&doknr=ISO+26262-8)*
*only requires measures if there is a risk that functional safety relevant faults*
*might be introduced into the product. Nevertheless with respect to the DROP*
*(delivery release of a product) there are additional product properties which*
*have to be accounted for (e.g. SOTIF, security, law compliance, data protection,*
*...) that might not effect functional safety. It is of big interest that tools*
*supporting these properties are also trustworthy. Therefore the scope of this*
*regulation is beyond [ISO 26262-8](https://rb-normen.bosch.com/NormMaster/DirectLink.do?ACTION=VIEW_STANDARD&doknr=ISO+26262-8)*
*and also includes all release relevant product aspects.*


## A3 Definition of Terms

**Tool**: See [tool definition](https://abt-prolib.de.bosch.com/stages/#/workspace/203/_vv/process/artifact/_hH4lANctWueYiciQ1WsBOg)
in ProLIB.

*Recommendation: The governing criterion for the definition of a tool should be*
*the use case. If a use case requires multiple SW programs, it is useful to*
*cluster them to one tool.*

![Tool definition](https://inside-share-hosted-apps.bosch.com/DMS/GetDocumentService/Document.svc/GetDocumentURL?documentID=P12S108958-930743451-8906)

**Tool project**: Activity within a project or created by the line organization
to develop a tool.

**Project**: In the scope of this regulation projects are activities according
[MP-201.01 XC Manage Product Development Projects](https://abt-prolib.de.bosch.com/stages/#/workspace/203/_vv/process/guidance/_OCMfQMsKEu-7DN4Sc9b6jQ)
that might include tool projects and use tools (e.g. platform project, customer
project, ...)

**Product**: In the scope of this regulation is the final product, which should
be launched on the market.

**Use case**: A use case describes the user's interaction with a tool or a
subset of the tool's features and the purpose of using the tool. It can
include requirements for the tool's configuration and the environment in which
the software tool is executed.

*Recommendation: A use case should be on a level of an activity or task of the product
life cycle (e.g. in engineering: Model system design, Perform unit test, Determine
ground truth data, ...)*

**Feature**: Features are intended to provide an additional structuring element
for the use cases which might ease evaluation and classification of the tool and
its use cases. As such features can be a solution or part of the solution which
will be implemented, sourced, ... during tool development. They can also be replaced
by sub-use cases. Features are optional elements in the classification and can be
omitted.


## A4 Additional information for project roles

Example for tool project roles:

| Domain       | Tool roles       | Designation       |
| ------------ | ---------------- | ----------------- |
| Tool project | Tool responsible | Person: Development engineer, PO, etc |
|              | Tool owner       | Line organization: Group, Department, etc |
|              | Sponsor          | Person: PjM, PO, etc |


## A5 Additional information for Decision on tool development

Expected costs and alternative tools can be specified in tabular form:

| Costs                      | Personal effort / person month | External costs / € |
| -------------------------- | -------------------------------| -------------------|
| Initial development effort |                                |                    |
| Annual maintenance effort  |                                |                    |


| Alternative tools          |                                              |
| -------------------------- | -------------------------------------------- |
| Tool                       | Benefit of planned tool                      |
| {{INPUT TOOL1}}            |                                              |
| {{INPUT TOOL2}}            |                                              |


## A6 Additional information for OSS

OSS usage shall be planned as early as possible to account for possible requirements.

If the tool contains OSS parts (packages or snippets) or introduces OSS
parts into the product, compliance with legal, license and customer OSS
obligations and requirements and the BU OSS strategy shall be achieved. In the
framework of tools development and usage, it is of high relevance, but not
exclusively, to consider whether shipping of the tool or parts of the tool to
another legal entity (e.g. RBEI, customer, ...) is planned.

The OSS shall be documented in the [TBOM template](https://abt-prolib.de.bosch.com/stages/#/workspace/203/_vv/process/guidance/_TWNDAOZvuMCJ1a8PMweTEA).

The following information shall be available:

* The OSS license
* The name/title of original OSS package or snippet
* The original source of each OSS aspect in the tool shall be documented
* the source of the oss relevant source code shall be available

The documentation can be supported by an open source scan. An open source scan shall
be conducted for the following scenarios:

* Tool introduces OSS parts in the product: OSS scan shall be provided to decide
on introduction based on potential disclosure requirements. (A detailed description
for such a scenario is provided in the [Method - Open Source Software Guideline](https://abt-prolib.de.bosch.com/stages/#/workspace/203/_vv/process/guidance/_vCcsUO7hk8K7DN4Sc9b6jQ).)
* Tool is shipped to non-RB legal entity: OSS scan shall be provided to decide on
shipping based on potential disclosure requirements.
* Tool is shipped to other RB legal entity:
    * If access to source code is provided: No additional requirements arise
    * If access to source code is not provided: OSS scan shall be provided to decide
    on shipping based on potential disclosure requirements.

An OSS scan shall be requested via [XC-OSS-Scan-Request](https://rb-tracker.bosch.com/tracker17/servicedesk/customer/portal/573/create/3814).
The details for source code handover are described [here](https://inside-docupedia.bosch.com/confluence/x/zbuwa).

Documentation shall be an ongoing process starting with the start of development.

OSS in third party components (COTS, instrument SW, ...) of the tool shall be
documented as well.

Further reading and information:

* [OSS Management XC](https://inside-docupedia.bosch.com/confluence/x/laB4B)
* [OSS@CC community](https://connect.bosch.com/communities/service/html/communitystart?communityUuid=6fc3c391-e98b-4c8e-8966-8be3e862cb25)
* RB-regulation on OSS: [CD04505 Open Source](https://rb-wam.bosch.com/socos-c/SOCOS/finder.cgi?CD-04505-000_VAW_X_XX)
* Overview over common OSS licenses and corresponding obligations:
[OSS Compliance Manager](http://oss-compliance-manager.bosch.com/)


## A7 Additional information for 3rd party software

*Note: Third party software also includes freeware and SW provided by customers.*

If the tool contains or introduces 3rd party SW (packages or snippets) the compliance
with license obligations and requirements shall be achieved.

The 3rd party SW shall be documented in the [TBOM template](https://abt-prolib.de.bosch.com/stages/#/workspace/203/_vv/process/guidance/_TWNDAOZvuMCJ1a8PMweTEA).

The following information shall be available:

* Identifier of the SW
* License terms of the SW
* Contract documents, if applicable
* Details of the license stock and its management, if applicable

The 3rd party software license shall be examined and provided to the
[Third Party Software Officer](https://abt-prolib.de.bosch.com/stages/#/workspace/203/_vv/process/role/_D2iO4IrUmLy7DN4Sc9b6jQ)
if it is used in the direct area or is provided by this tool project. If the 3rd
party software is used in the indirect area and is centrally provided (e.g. by CI)
the providing entity has to examine the license terms in this case.

Requirements and details are defined in the RB-regulation on third party software:
[CD03016 Software License Management](https://rb-wam.bosch.com/socos-c/SOCOS/finder.cgi?CD-03016-000_VAW_X_XX)


## A8 Additional information for Data protection relevance

Definition and examples of personal data is available in
[CD02900-001](https://rb-wam.bosch.com/socos-c/SOCOS/finder.cgi?CD-02900-001_ANH_X_EN).

Responsible BER-board for location Abstatt: [Technology & Digitalization](https://connect.bosch.com/wikis/home?lang=de-de#!/wiki/Waf466a7ab058_4284_b134_8a1d65e32c68/page/TD%20(Technologie%20%26%20Digitalisierung))


## A9 Additional information for Configuration management

The tool might include the functionality to writing a unique identifier (e.g.
release version, commit tag, ...) into all dumped artifacts. It might also dump a
tool configuration file with any artefact.


## A10 Additional information for Quality assurance

The following list contains methods and measures for quality assurance of tool
development, which are recommended for use in tool development depending on size
and qualification of the tool project:

* Review: code, design, requirements
* Statistical code analysis, tool supported (e.g. Coverity)
* Use of tools to ensure adherence to Coding rules (e.g. QAC)
* Module, component, integration and system tests
* Lessons Learned processes, error management
* Pair programming


## A11 Additional information for Tool release

A release must at least contain:

* Documentation of taken quality assurance measures
* Documentation of quality status of the measures
* Documentation of deviations from tool quality assurance plan, if applicable
* Documentation of usage constraints, malfunctions and limitation of
the tool
* Documentation of the OSS, third party software and hardware of the tool according
to the [TBOM template](https://abt-prolib.de.bosch.com/stages/#/workspace/203/_vv/process/guidance/_TWNDAOZvuMCJ1a8PMweTEA)
* Documentation of obligations of the tool specifically but none-exclusive resulting
from ...
    * OSS and third party software licenses
    * quality assurance
* Documentation of the valid TDP version (including valid TDP artifacts) for
each release in case multiple TDP versions exist
* Documentation of dependencies for tool operation (e.g. specific version of
operation systems, COTS, ...), if applicable
* Documentation of [SW consulting service](https://www.intranet.bosch.com/app/swc/webrequest/frm_SoftwareRequest.aspx)
for used SW (COTS, Freeware, OSS, ...), if applicable


Minimum requirement is to write a Readme.txt, which at least contains the above
defined minimum standard. Store it in location with the release.

It shall be assured that the storage of all documents is compliant to the
[ISP Retention Period Management Tool (Virgo)](https://rb-wam.bosch.com/isp-portal/#/rpm-tools)
As the TDP and relevant tool artifacts (content under config management) are product liability relevant, a
storage period of 15 years from the end of the period in which they are used is
required. If the end of the period in which they are used cannot be determined
35 years are required.


## A12 Additional information on ISO 26262 compliance

A good practice for classification is provided in the BoCo
[Tool Processes @XC-DX](https://connect.bosch.com/communities/service/html/communitystart?communityUuid=63699805-8865-44b6-8697-5a6a902866a8).

Guidance on classification is provided by the RB norm [N102 FS004](https://rb-normen.bosch.com/NormMaster/DirectLink.do?ACTION=VIEW_STANDARD&doknr=N102+FS004).

Guidance on qualification is provided by the RB norm
[N102 FS005](https://rb-normen.bosch.com/NormMaster/DirectLink.do?ACTION=VIEW_STANDARD&doknr=N102+FS005).

In case of TCL2 or TCL3 it is recommended to apply a combination of two
[ISO 26262-8](https://rb-normen.bosch.com/NormMaster/DirectLink.do?ACTION=VIEW_STANDARD&doknr=ISO+26262-8)
quality measures. The defined tool development process is considered as an
appropriate standard. Therefore the documentation of the process serves as
evidence for the ISO 26262-8 qualification method "evaluation of the tool
development process". "Validation of the tool" is required for the remaining
measure. Both shall be documented in the Quality Assurance section.

ISO 26262 compliance is a joint task. The following information is of high
importance. The roles in brackets provide an indication which role most likely
is capable to provide it:

* Deep understanding of the tool itself (Tool responsible)
* Specific use cases of the tool in the project (Tool user)
* Impact of tool malfunction on product safety (Safety expert)
* Likelihood of tool error detection within development process of the project
(Process expert)

As per this tool development process the tool responsible is responsible for
the coordination. The entitled roles shall contribute on demand. Otherwise,
compliance cannot be achieved.