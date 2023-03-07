# pylint: disable=too-many-lines, too-many-public-methods
"""
This module contains a functional wrapper of the API for ICoCo specifications

Warning
-------
    This is an experimental module.

It supports proper management of the TIME_STEP_CONTEXT and scope of usage of the methods.
"""

import os
from typing import List, Tuple

from icoco.utils import ICOCO_MAJOR_VERSION, ValueType, MPIComm # type: ignore
try:
    from icoco.utils import medcoupling
except ImportError:
    pass
from icoco.exception import WrongArgument, WrongContext
from icoco.problem import Problem

class ProblemWrapper:
    """Minimal implementation of ICoCo problem."""

    @staticmethod
    def GetICoCoMajorVersion() -> int:
        """Return ICoCo interface major version number.

        Returns
        -------
        int
            ICoCo interface major version number (icoco.ICOCO_MAJOR_VERSION)
        """
        return ICOCO_MAJOR_VERSION

    class Context:
        """Define an ICoCo time step context."""

        def __init__(self) -> None:

            self._time: float = 0.0
            """Current (physical) time"""
            self._dt: float = 0.0
            """Current Time step"""
            self._inside: bool = False
            """Current context"""
            self._stationnary: bool = False
            """Stationnary mode"""

        def reset_time(self, time: float):
            """Resets the current time

            Parameters
            ----------
            time : float
                New current (physical) time
            """
            self._time = time

        def initialize_step(self, dt: float):
            """initializes the time step (enter context + store dt)

            Parameters
            ----------
            dt : float
                Time step
            """
            self._dt = dt
            self._inside = True

        def validate_step(self):
            """Increment time and exits context
            """
            self._time += self._dt
            self.abort_step()

        def abort_step(self):
            """Reset dt and exits context
            """
            self._dt = 0.0
            self._inside = False

        @property
        def time_step_defined(self) -> bool:
            """Returns context"""
            return self._inside

        @property
        def dt(self) -> float:
            """Returns current dt
            """
            return self._dt

        @property
        def time(self) -> float:
            """Returns current time
            """
            return self._time

        def set_stationnary(self, stationnary: bool):
            """Stores stationary mode"""
            self._stationnary = stationnary

        @property
        def stationnary(self) -> bool:
            """Returns stationnary mode"""
            return self._stationnary


    # ******************************************************
    # section Problem
    # ******************************************************

    def __init__(self, impl: Problem) -> None:
        """Constructor.

        Notes
        -----
            Internal set up and initialization of the code should not be done here,
            but rather in initialize() method.

        Parameters
        ----------
        impl : Problem
            problem implmentation.
        """

        self._impl: Problem = impl

        self._data_file: str = None # type: ignore
        """Argumrent provided to setDataFile method"""

        self._mpicomm: MPIComm = None # type: ignore
        """Argumrent provided to setMPIComm method"""

        self._context: ProblemWrapper.Context = None # type: ignore
        """Time step management"""

    def setDataFile(self, datafile: str) -> None:
        """(Optional) Provide the relative path of a data file to be used by the code.

        This method must be called before initialize().

        Parameters
        ----------
        datafile : str
            relative path to the data file.

        Raises
        ------
        icoco.WrongContext
            exception if called multiple times or after initialize().
        icoco.WrongArgument
            exception if an invalid path is provided.
        """

        if not os.path.exists(datafile):
            raise WrongArgument(prob=self._impl.problem_name,
                                method="setDataFile",
                                arg="datafile",
                                condition="invalid path is provided",
                                )

        if self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="setDataFile",
                               precondition="called after initialize()")

        if self._data_file is not None:
            raise WrongContext(prob=self._impl.problem_name,
                               method="setDataFile",
                               precondition="called multiple times")

        self._impl.setDataFile(datafile)

    def setMPIComm(self, mpicomm: MPIComm) -> None:
        """(Optional) Provide the MPI communicator to be used by the code for parallel computations.

        This method must be called before initialize(). The communicator should include all the
        processes to be used by the code. For a sequential code, the call to setMPIComm is optional
        or mpicomm should be None.

        Parameters
        ----------
        mpicomm : MPIComm
            MPI communicator. Dummy type for codes without mpi4py.

        Raises
        ------
        icoco.WrongContext
            exception if called multiple times or after initialize().
        icoco.WrongArgument
            exception if an invalid path is provided.
        """

        if self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="setMPIComm",
                               precondition="called after initialize()")

        if self._mpicomm is not None:
            raise WrongContext(prob=self._impl.problem_name,
                               method="setMPIComm",
                               precondition="called multiple times")

        self._impl.setMPIComm(mpicomm)

    def initialize(self) -> bool:
        """(Mandatory) Initialize the current problem instance.

        In this method the code should allocate all its internal structures and be ready to execute.
        File reads, memory allocations, and other operations likely to fail should be performed
        here, and not in the constructor (and not in the setDataFile() or in the setMPIComm()
        methods either).
        This method must be called only once (after a potential call to setMPIComm() and/or
        setDataFile()) and cannot be called again before terminate() has been performed.

        Returns
        -------
        bool
            true if all OK, otherwise false.

        Raises
        ------
        WrongContext
            exception if called multiple times or after initialize().
        """

        if self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="initialize",
                               precondition="called multiple times or after initialize()")

        self._context = ProblemWrapper.Context()

        return self._impl.initialize()

    def terminate(self) -> None:
        """(Mandatory) Terminate the current problem instance and release all allocated resources.

        Terminate the computation, free the memory and save whatever needs to be saved.
        This method is called once at the end of the computation or after a non-recoverable error.
        No other ICoCo method except setDataFile(), setMPIComm() and initialize() may be called
        after this.

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
            exception if called inside the TIME_STEP_DEFINED context (see Problem documentation).
        """

        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="terminate",
                               precondition="called before initialize() or after terminate()")

        if self._context.time_step_defined:
            raise WrongContext(prob=self._impl.problem_name,
                               method="terminate",
                               precondition="called inside the TIME_STEP_DEFINED context"
                                            " (see Problem documentation)")

        self._impl.terminate()

        self._context = None # type: ignore

    # ******************************************************
    # section TimeStepManagement
    # ******************************************************

    def presentTime(self) -> float:
        """(Mandatory) Return the current time of the simulation.

        Can be called any time between initialize() and terminate().
        The current time can only change during a call to validateTimeStep() or to resetTime().

        Notes
        ----_
            This method doesn't call the implementation interface.

        Returns
        -------
        float
            the current (physical) time of the simulation

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        """

        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="presentTime",
                               precondition="called before initialize() or after terminate()")

        return self._context.time

    def computeTimeStep(self) -> Tuple[float, bool]:
        """(Mandatory) Return the next preferred time step (time increment) for this code, and
        whether the code wants to stop.

        Both data are only indicative, the supervisor is not required to take them into account.
        This method is however marked as mandatory, since most of the coupling schemes expect the
        code to provide this information (those schemes then typically compute the minimum of the
        time steps of all the codes being coupled). Hence a possible implementation is to return a
        huge value, if a precise figure can not be computed.

        Can be called whenever the code is outside the TIME_STEP_DEFINED context (see Problem
        documentation).

        Returns
        -------
        Tuple[float, bool]
            - the preferred time step for this code (only valid if stop is false).
            - stop set to true if the code wants to stop. It can be used for example to indicate
              that, according to a certain criterion, the end of the transient computation is
              reached from the code point of view.

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
            exception if called inside the TIME_STEP_DEFINED context (see Problem documentation).
        """

        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="terminate",
                               precondition="called before initialize() or after terminate()")

        if self._context.time_step_defined:
            raise WrongContext(prob=self._impl.problem_name,
                               method="terminate",
                               precondition="called inside the TIME_STEP_DEFINED context."
                                            " (see Problem documentation)")

        return self._impl.computeTimeStep()

    def initTimeStep(self, dt: float) -> bool:
        """(Mandatory) Provide the next time step (time increment) to be used by the code.

        After this call (if successful), the computation time step is defined to ]t, t + dt] where
        t is the value returned by presentTime(). The code enters the TIME_STEP_DEFINED context.

        A time step = 0.0 may be used when the stationaryMode is set to true for codes solving
        directly for the steady-state.

        Parameters
        ----------
        dt : float
            dt the time step to be used by the code

        Returns
        -------
        bool
            false means that given time step is not compatible with the code time scheme.

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
            exception if called inside the TIME_STEP_DEFINED context (see Problem documentation).
            exception if called several times without resolution.
        WrongArgument
            exception if dt is invalid (dt < 0.0).
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="initTimeStep",
                               precondition="called before initialize() or after terminate()")

        if self._context.time_step_defined:
            raise WrongContext(prob=self._impl.problem_name,
                               method="initTimeStep",
                               precondition="called inside the TIME_STEP_DEFINED context."
                                            " (see Problem documentation)")

        if dt < 0.0:
            raise WrongArgument(prob=self._impl.problem_name,
                               method="initTimeStep",
                               arg="dt",
                               condition=f"dt={dt} is invalid (dt < 0.0)")

        self._context.initialize_step(dt)

        return self._impl.initTimeStep(dt)

    def solveTimeStep(self) -> bool:
        """(Mandatory) Perform the computation on the current time interval.

        Can be called whenever the code is inside the TIME_STEP_DEFINED context
        (see Problem documentation).

        Returns
        -------
        bool
            true if computation was successful, false otherwise.

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
            exception if called outside the TIME_STEP_DEFINED context (see Problem documentation).
            exception exception if called several times without a call to validateTimeStep() or to
            abortTimeStep().
        """

        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="solveTimeStep",
                               precondition="called before initialize() or after terminate()")

        if not self._context.time_step_defined:
            raise WrongContext(prob=self._impl.problem_name,
                               method="solveTimeStep",
                               precondition="called outside the TIME_STEP_DEFINED context."
                                            " (see Problem documentation)")

        return self._impl.solveTimeStep()

    def validateTimeStep(self) -> None:
        """(Mandatory) Validate the computation performed by solveTimeStep.

        Can be called whenever the code is inside the TIME_STEP_DEFINED context (see Problem
        documentation).

        After this call:
        - the present time has been advanced to the end of the computation time step
        - the computation time step is undefined (the code leaves the TIME_STEP_DEFINED context).

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
            exception if called outside the TIME_STEP_DEFINED context (see Problem documentation).
            exception if called before the solveTimeStep() method.
        """

        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="validateTimeStep",
                               precondition="called before initialize() or after terminate()")

        if not self._context.time_step_defined:
            raise WrongContext(prob=self._impl.problem_name,
                               method="validateTimeStep",
                               precondition="called outside the TIME_STEP_DEFINED context."
                                            " (see Problem documentation)")

        self._impl.validateTimeStep()

        self._context.validate_step()

    def setStationaryMode(self, stationaryMode: bool) -> None:
        """(Mandatory) Set whether the code should compute a stationary solution or a transient one.

        New in version 2 of ICoCo. By default the code is assumed to be in stationary mode False
        (i.e. set up for a transient computation).
        If set to True, solveTimeStep() can be used either to solve a time step in view of an
        asymptotic solution, or to solve directly for the steady-state. In this last case, a time
        step = 0. can be used with initTimeStep() (whose call is always needed).
        The stationary mode status of the code can only be modified by this method (or by a call to
        terminate() followed by initialize()).

        Can be called whenever the code is outside the TIME_STEP_DEFINED context
        (see Problem documentation).

        Parameters
        ----------
        stationaryMode : bool
            true if the code should compute a stationary solution.

        Raises
        ------
        WrongContext
            called inside the TIME_STEP_DEFINED context (see Problem documentation).
            called before initialize() or after terminate().
        """

        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="setStationaryMode",
                               precondition="called before initialize() or after terminate()")

        if self._context.time_step_defined:
            raise WrongContext(prob=self._impl.problem_name,
                               method="setStationaryMode",
                               precondition="called inside the TIME_STEP_DEFINED context."
                                            " (see Problem documentation)")

        self._impl.setStationaryMode(stationaryMode=stationaryMode)
        self._context.set_stationnary(stationnary=stationaryMode)

    def getStationaryMode(self) -> bool:
        """(Mandatory) Indicate whether the code should compute a stationary solution or a
        transient one.

        See also setStationaryMode().

        Can be called whenever the code is outside the TIME_STEP_DEFINED context
        (see Problem documentation). -> NOT APPLIED IN THIS IMPLEMENTATION.

        Notes
        -----
            This method doesn't call the implementation interface.

        Returns
        -------
        bool
            true if the code has been set to compute a stationary solution.

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
            exception if called inside the TIME_STEP_DEFINED context (see Problem documentation)
            (NOT APPLIED IN THIS IMPLEMENTATION).
        """

        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getStationaryMode",
                               precondition="called before initialize() or after terminate()")

        return self._context.stationnary

    def isStationary(self) -> bool:
        """(Optional) Return whether the solution is constant on the computation time step.

        Used to know if the steady-state has been reached. This method can be called whenever the
        computation time step is not defined.

        Returns
        -------
        bool
            true if the solution is constant on the computation time step.

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
            exception if called inside the TIME_STEP_DEFINED context (see Problem documentation),
            meaning we shouldn't request this information while the computation of a new time
            step is in progress.
        """

        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="isStationary",
                               precondition="called before initialize() or after terminate()")

        if self._context.time_step_defined:
            raise WrongContext(prob=self._impl.problem_name,
                               method="isStationary",
                               precondition="called inside the TIME_STEP_DEFINED context."
                                            " (see Problem documentation)")

        return self._impl.isStationary()

    def abortTimeStep(self) -> None:
        """(Optional) Abort the computation on the current time step.

        Can be called whenever the computation time step is defined, instead of validateTimeStep().
        After this call, the present time is left unchanged, and the computation time step is
        undefined (the code leaves the TIME_STEP_DEFINED context).

        You MUST call this method in the derived class. Exemple of implementation:

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
             exception if called outside the TIME_STEP_DEFINED context (see Problem documentation).
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="abortTimeStep",
                               precondition="called before initialize() or after terminate()")

        if not self._context.time_step_defined:
            raise WrongContext(prob=self._impl.problem_name,
                               method="abortTimeStep",
                               precondition="called outside the TIME_STEP_DEFINED context."
                                            " (see Problem documentation)")

        self._context.abort_step()
        self._impl.abortTimeStep()

    def resetTime(self, time: float) -> None:
        """(Optional) Reset the current time of the Problem to a given value.

        New in version 2 of ICoCo.
        Particularly useful for the initialization of complex transients: the starting point of the
        transient of interest is computed first, the time is reset to 0, and then the actual
        transient of interest starts with proper initial conditions, and global time 0.

        Can be called outside the TIME_STEP_DEFINED context (see Problem documentation).

        Parameters
        ----------
        time : float
            the new current time.

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
            exception if called inside the TIME_STEP_DEFINED context (see Problem documentation)
        """

        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="resetTime",
                               precondition="called before initialize() or after terminate()")

        if self._context.time_step_defined:
            raise WrongContext(prob=self._impl.problem_name,
                               method="resetTime",
                               precondition="called inside the TIME_STEP_DEFINED context."
                                            " (see Problem documentation)")

        self._context.reset_time(time=time)
        self._impl.resetTime(time=time)

    def iterateTimeStep(self) -> Tuple[bool, bool]:
        """(Optional) Perform a single iteration of computation inside the time step.

        This method is relevant for codes having inner iterations for the computation of a single
        time step.
        Calling iterateTimeStep() until converged is true is equivalent to calling
        solveTimeStep(), within the code's convergence threshold.

        Can be called (potentially several times) inside the TIME_STEP_DEFINED context
        (see Problem documentation).

        Returns
        -------
        Tuple[bool, bool]
            - false if the computation failed.
            - true if the solution is not evolving any more.

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
            exception if called outside the TIME_STEP_DEFINED context (see Problem documentation)
        """

        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="iterateTimeStep",
                               precondition="called before initialize() or after terminate()")

        if not self._context.time_step_defined:
            raise WrongContext(prob=self._impl.problem_name,
                               method="iterateTimeStep",
                               precondition="called outside the TIME_STEP_DEFINED context."
                                            " (see Problem documentation)")
        return self._impl.iterateTimeStep()

    # ******************************************************
    # section Restorable
    # ******************************************************
    def save(self, label: int, method: str) -> None:
        """(Optional) Save the state of the code.

        The saved state is identified by the combination of label and method arguments.
        If save() has already been called with the same two arguments, the saved state is
        overwritten.
        This method is const indicating that saving the state of the code should not change its
        behaviour with respect to all other ICoCo methods. Implementation may rely on a mutable
        attribute (e.g. if saving to memory is desired).

        Parameters
        ----------
        label : int
            a user- (or code-) defined value identifying the state.
        method : str
            a string specifying which method is used to save the state of the code. A code can
                provide different methods (for example in memory, on disk, etc.).

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
            exception if called inside the TIME_STEP_DEFINED context (see Problem documentation)
            meaning we shouldn't save a previous time step while the computation of a new time
            step is in progress.
        WrongArgument
            exception if the method or label argument is invalid.
        """

        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="save",
                               precondition="called before initialize() or after terminate()")

        if self._context.time_step_defined:
            raise WrongContext(prob=self._impl.problem_name,
                               method="save",
                               precondition="called inside the TIME_STEP_DEFINED context."
                                            " (see Problem documentation)")

        self._impl.save(label=label, method=method)

    def restore(self, label: int, method: str) -> None:
        """(Optional) Restore the state of the code.

        After restore, the code should behave exactly like after the corresponding call to save
        (except of course for save/restore methods, since the list of saved states may have
        changed).
        The state to be restored is identified by the combination of label and method arguments.
        The save() method must have been called at some point or in some previous run with this
        combination.

        Parameters
        ----------
        label : int
            a user- (or code-) defined value identifying the state.
        method : str
            a string specifying which method is used to save the state of the code. A code can
                provide different methods (for example in memory, on disk, etc.).

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
            exception if called inside the TIME_STEP_DEFINED context (see Problem documentation)
            meaning we shouldn't restore while the computation of a new time step is in
            progress.
        WrongArgument
            exception if the method or label argument is invalid.
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="restore",
                               precondition="called before initialize() or after terminate()")

        if self._context.time_step_defined:
            raise WrongContext(prob=self._impl.problem_name,
                               method="restore",
                               precondition="called inside the TIME_STEP_DEFINED context."
                                            " (see Problem documentation)")

        self.restore(label=label, method=method)

    def forget(self, label: int, method: str) -> None:
        """(Optional) Discard a previously saved state of the code.

        After this call, the save-point cannot be restored anymore. This method can be used to free
        the space occupied by unused saved states.
        This method is const indicating that forgeting a previous state of the code should not
        change its behaviour with respect to all other ICoCo methods. Implementation may rely on a
        mutable attribute (e.g. if saving to memory is desired).

        Parameters
        ----------
        label : int
            a user- (or code-) defined value identifying the state.
        method : str
            a string specifying which method is used to save the state of the code. A code can
                provide different methods (for example in memory, on disk, etc.).

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        WrongArgument
            exception if the method or label argument is invalid.
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="forget",
                               precondition="called before initialize() or after terminate()")

        self.forget(label=label, method=method)


    # ******************************************************
    # section Field I/O. Reminder: all methods are **optional**
    # not all of them need to be implemented!
    # ******************************************************

    def getInputFieldsNames(self) -> List[str]:
        """(Optional) Get the list of input fields accepted by the code.

        Returns
        -------
        List[str]
            the list of field names that represent inputs of the code

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        """

        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getInputFieldsNames",
                               precondition="called before initialize() or after terminate()")

        return self._impl.getInputFieldsNames()

    def getOutputFieldsNames(self) -> List[str]:
        """(Optional) Get the list of output fields that can be provided by the code.

        Returns
        -------
        List[str]
            the list of field names that can be produced by the code

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getOutputFieldsNames",
                               precondition="called before initialize() or after terminate()")

        return self._impl.getOutputFieldsNames()

    def getFieldType(self, name: str) -> ValueType:
        """(Optional) Get the type of a field managed by the code (input or output)

        The three possible types are int, double and string, as defined in the ValueType enum.

        Parameters
        ----------
        name : str
            field name

        Returns
        -------
        ValueType
            one of ValueType.Double, ValueType.Int or ValueType.String

        Raises
        ------
        WrongArgument
            exception if the field name is invalid.
        WrongContext
            exception if called before initialize() or after terminate().
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getFieldType",
                               precondition="called before initialize() or after terminate()")

        return self._impl.getFieldType(name=name)

    def getMeshUnit(self) -> str:
        """(Optional) Get the (length) unit used to define the meshes supporting the fields.

        Returns
        -------
        str
            length unit in which the mesh coordinates should be understood (e.g. "m", "cm", ...)

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getMeshUnit",
                               precondition="called before initialize() or after terminate()")

        return self._impl.getMeshUnit()

    def getFieldUnit(self, name: str) -> str:
        """(Optional) Get the physical unit used for a given field.

        Parameters
        ----------
        name : str
            field name

        Returns
        -------
        str
            unit in which the field values should be understood (e.g. "W", "J", "Pa", ...)

        Raises
        ------
        WrongArgument
            exception if the field name is invalid.
        WrongContext
            exception if called before initialize() or after terminate().
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getFieldUnit",
                               precondition="called before initialize() or after terminate()")

        return self._impl.getFieldUnit(name)

    # ******************************************************
    #     subsection MED*Field fields I/O
    # ******************************************************

    def getInputMEDDoubleFieldTemplate(self, name: str) -> 'medcoupling.MEDCouplingFieldDouble':
        """(Optional) Retrieve an empty shell for an input field. This shell can be filled by the
        caller and then be given to the code via setInputField(). The field has the MEDDoubleField
        format.

        The code uses this method to populate 'afield' with all the data that represents the context
        of the field (i.e. its support mesh, its discretization -- on nodes, on elements, ...).
        The remaining job for the caller of this method is to fill the actual values of the field
        itself.
        When this is done the field can be sent back to the code through the method setInputField().
        This method is not mandatory but is useful to know the mesh, discretization... on which an
        input field is expected.

        See Problem documentation for more details on the time semantic of a field.

        Parameters
        ----------
        name : str
            name of the field for which we would like the empty shell

        Returns
        -------
        medcoupling.MEDCouplingFieldDouble
            field object (in MEDDoubleField format) that will be populated with all the contextual
            information.
            Any previous information in this object will be discarded.

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        WrongArgument
            exception if the field name is invalid.
        """

        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getInputMEDDoubleFieldTemplate",
                               precondition="called before initialize() or after terminate()")

        return self._impl.getInputMEDDoubleFieldTemplate(name)

    def setInputMEDDoubleField(self, name: str, afield: 'medcoupling.MEDCouplingFieldDouble') -> None:
        """(Optional) Provide the code with input data in the form of a MEDDoubleField.

        The method getInputFieldTemplate(), if implemented, may be used first to prepare an empty
        shell of the field to pass to the code.

        See Problem documentation for more details on the time semantic of a field.

        Parameters
        ----------
        name : str
            name of the field that is given to the code.
        afield : medcoupling.MEDCouplingFieldDouble
            field object (in MEDDoubleField format) containing the input data to be read by the
            code. The name of the field set on this instance (with the Field::setName() method)
            should not be checked. However its time value should be to ensure it is within the
            proper time interval ]t, t+dt].


        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        WrongArgument
            exception if the field name ('name' parameter) is invalid.
            exception if the time property of 'afield' does not belong to the currently computed
            time step ]t, t + dt]
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="setInputMEDDoubleField",
                               precondition="called before initialize() or after terminate()")

        return self._impl.setInputMEDDoubleField(name=name, afield=afield)


    def getOutputMEDDoubleField(self, name: str) -> 'medcoupling.MEDCouplingFieldDouble':
        """(Optional) Retrieve output data from the code in the form of a MEDDoubleField.

        Gets the output field corresponding to name from the code into the afield argument.

        See Problem documentation for more details on the time semantic of a field.

        Parameters
        ----------
        name : str
            name of the field that the caller requests from the code.

        Returns
        -------
        medcoupling.MEDCouplingFieldDouble
            field object (in MEDDoubleField format) populated with the data read by the code.
            The name and time properties of the field should be set in accordance with the 'name'
            parameter and with the current time step being computed.
            Any previous information in this object will be discarded.

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        WrongArgument
            exception if the field name ('name' parameter) is invalid.
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getOutputMEDDoubleField",
                               precondition="called before initialize() or after terminate()")
        return self._impl.getOutputMEDDoubleField(name=name)

    def updateOutputMEDDoubleField(self,
                                   name: str,
                                   afield: 'medcoupling.MEDCouplingFieldDouble') -> None:
        """(Optional) Update a previously retrieved output field.

        (New in version 2) This methods allows the code to implement a more efficient update of a
        given output field, thus avoiding the caller to invoke getOutputMEDDoubleField() each time.
        A previous call to getOutputMEDDoubleField() with the same name must have been done prior to
        this call.
        The code should check the consistency of the field object with the requested data
        (same support mesh, discretization -- on nodes, on elements, etc.).

        See Problem documentation for more details on the time semantic of a field.

        Parameters
        ----------
        name : str
            name of the field that the caller requests from the code.
        afield : medcoupling.MEDCouplingFieldDouble
            field object (in MEDDoubleField format) updated with the data read from the code.
            Notably the time indicated in the field should be updated to be within the current time
            step being computed.

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        WrongArgument
            exception if the field name ('name' parameter) is invalid.
            exception if the field object is inconsistent with the field being requested.
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="updateOutputMEDDoubleField",
                               precondition="called before initialize() or after terminate()")
        return self._impl.updateOutputMEDDoubleField(name=name, afield=afield)

    def getInputMEDIntFieldTemplate(self, name: str) -> 'medcoupling.MEDCouplingFieldInt':
        """Similar to getInputMEDDoubleFieldTemplate() but for MEDIntField.

        See Also
        --------
            getInputMEDDoubleFieldTemplate

        Parameters
        ----------
        name : str
            name of the field for which we would like the empty shell

        Returns
        -------
        medcoupling.MEDCouplingFieldInt
            object

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        WrongArgument
            exception if the field name is invalid.
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getInputMEDIntFieldTemplate",
                               precondition="called before initialize() or after terminate()")

        return self._impl.getInputMEDIntFieldTemplate(name)

    def setInputMEDIntField(self, name: str, afield: 'medcoupling.MEDCouplingFieldInt') -> None:
        """Similar to setInputMEDDoubleField() but for MEDIntField.

        See Also
        --------
            setInputMEDDoubleField

        Parameters
        ----------
        name : str
            name of the field that is given to the code.
        afield : medcoupling.MEDCouplingFieldInt
            field object

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        WrongArgument
            exception if the field name ('name' parameter) is invalid.
            exception if the time property of 'afield' does not belong to the currently computed
            time step ]t, t + dt]
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="setInputMEDIntField",
                               precondition="called before initialize() or after terminate()")

        return self._impl.setInputMEDIntField(name=name, afield=afield)

    def getOutputMEDIntField(self, name: str) -> 'medcoupling.MEDCouplingFieldInt':
        """Similar to getOutputMEDDoubleField() but for MEDIntField.

        See Also
        --------
            getOutputMEDDoubleField

        Parameters
        ----------
        name : str
            name of the field that the caller requests from the code.

        Returns
        -------
        medcoupling.MEDCouplingFieldInt
            field object

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        WrongArgument
            exception if the field name ('name' parameter) is invalid.
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getOutputMEDIntField",
                               precondition="called before initialize() or after terminate()")

        return self._impl.getOutputMEDIntField(name=name)

    def updateOutputMEDIntField(self,
                                   name: str,
                                   afield: 'medcoupling.MEDCouplingFieldInt') -> None:
        """Similar to getInputMEDDoubleFieldTemplate() but for MEDStringField.

        See Also
        --------
            getInputMEDDoubleFieldTemplate

        Parameters
        ----------
        name : str
            name of the field that the caller requests from the code.
        afield : medcoupling.MEDCouplingFieldInt
            field object

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        WrongArgument
            exception if the field name ('name' parameter) is invalid.
            exception if the field object is inconsistent with the field being requested.
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="updateOutputMEDIntField",
                               precondition="called before initialize() or after terminate()")

        return self._impl.updateOutputMEDIntField(name, afield)

    def getInputMEDStringFieldTemplate(self, name: str) -> 'medcoupling.MEDCouplingField':
        """Similar to getInputMEDDoubleFieldTemplate() but for MEDStringField.

        Warning
        -------
            at the time of writing, MEDStringField are not yet implemented anywhere.

        See Also
        --------
            getInputMEDDoubleFieldTemplate

        Parameters
        ----------
        name : str
            name of the field for which we would like the empty shell

        Returns
        -------
        medcoupling.MEDCouplingFieldString
            object

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        WrongArgument
            exception if the field name is invalid.
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getInputMEDStringFieldTemplate",
                               precondition="called before initialize() or after terminate()")

        return self._impl.getInputMEDStringFieldTemplate(name)

    def setInputMEDStringField(self, name: str, afield: 'medcoupling.MEDCouplingField') -> None:
        """Similar to setInputMEDDoubleField() but for MEDStringField.

        Warning
        -------
            at the time of writing, MEDStringField are not yet implemented anywhere.

        See Also
        --------
            setInputMEDDoubleField

        Parameters
        ----------
        name : str
            name of the field that is given to the code.
        afield : medcoupling.MEDCouplingFieldString
            field object

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        WrongArgument
            exception if the field name ('name' parameter) is invalid.
            exception if the time property of 'afield' does not belong to the currently computed
            time step ]t, t + dt]
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="setInputMEDStringField",
                               precondition="called before initialize() or after terminate()")

        return self._impl.setInputMEDStringField(name=name, afield=afield)

    def getOutputMEDStringField(self, name: str) -> 'medcoupling.MEDCouplingField':
        """Similar to getOutputMEDDoubleField() but for MEDStringField.

        Warning
        -------
            at the time of writing, MEDStringField are not yet implemented anywhere.

        See Also
        --------
            getOutputMEDDoubleField

        Parameters
        ----------
        name : str
            name of the field that the caller requests from the code.

        Returns
        -------
        medcoupling.MEDCouplingFieldString
            field object

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        WrongArgument
            exception if the field name ('name' parameter) is invalid.
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getOutputMEDStringField",
                               precondition="called before initialize() or after terminate()")

        return self._impl.getOutputMEDStringField(name=name)

    def updateOutputMEDStringField(self,
                                   name: str,
                                   afield: 'medcoupling.MEDCouplingField') -> None:
        """Similar to getInputMEDDoubleFieldTemplate() but for MEDStringField.

        Warning
        -------
            at the time of writing, MEDStringField are not yet implemented anywhere.

        See Also
        --------
            getInputMEDDoubleFieldTemplate

        Parameters
        ----------
        name : str
            name of the field that the caller requests from the code.
        afield : medcoupling.MEDCouplingFieldString
            field object

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        WrongArgument
            exception if the field name ('name' parameter) is invalid.
            exception if the field object is inconsistent with the field being requested.
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="updateOutputMEDStringField",
                               precondition="called before initialize() or after terminate()")

        return self._impl.updateOutputMEDStringField(name, afield)

    def getMEDCouplingMajorVersion(self) -> int:
        """(Optional) Get MEDCoupling major version, if the code was built with MEDCoupling support.

        This can be used to assess compatibility between codes when coupling them.

        Returns
        -------
        int
            the MEDCoupling major version number (typically 7, 8, 9, ...)
        """
        return self._impl.getMEDCouplingMajorVersion()

    def isMEDCoupling64Bits(self) -> bool:
        """(Optional) (Optional) Indicate whether the code was built with a 64-bits version of
        MEDCoupling.

        Implemented if the code was built with MEDCoupling support.
        This can be used to assess compatibility between codes when coupling them.

        Returns
        -------
        bool
            True if it is 64-bits
        """
        return self._impl.isMEDCoupling64Bits()

    # ******************************************************
    # section Scalar values I/O
    # ******************************************************

    def getInputValuesNames(self) -> List[str]:
        """(Optional) Get the list of input scalars accepted by the code.

        Returns
        -------
        List[str]
            the list of scalar names that represent inputs of the code

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        """

        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getInputValuesNames",
                               precondition="called before initialize() or after terminate()")

        return self._impl.getInputValuesNames()

    def getOutputValuesNames(self) -> List[str]:
        """(Optional) Get the list of output scalars that can be provided by the code.

        Returns
        -------
        List[str]
            the list of scalars names that can be produced by the code

        Raises
        ------
        WrongContext
            exception if called before initialize() or after terminate().
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getOutputValuesNames",
                               precondition="called before initialize() or after terminate()")

        return self._impl.getOutputValuesNames()

    def getValueType(self, name: str) -> ValueType:
        """(Optional)  Get the type of a scalar managed by the code (input or output)

        The three possible types are int, double and string, as defined in the ValueType enum.

        Parameters
        ----------
        name : str
            scalar value name

        Returns
        -------
        ValueType
            one of ValueType.Double, ValueType.Int or ValueType.String

        Raises
        ------
        WrongArgument
            exception if the field name is invalid.
        WrongContext
            exception if called before initialize() or after terminate().
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getValueType",
                               precondition="called before initialize() or after terminate()")

        return self._impl.getValueType(name=name)


    def getValueUnit(self, name: str) -> str:
        """(Optional) Get the physical unit used for a given value.

        Parameters
        ----------
        name : str
            scalar value name

        Returns
        -------
        str
            unit in which the field values should be understood (e.g. "W", "J", "Pa", ...)

        Raises
        ------
        WrongArgument
            exception if the field name is invalid.
        WrongContext
            exception if called before initialize() or after terminate().
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getFieldUnit",
                               precondition="called before initialize() or after terminate()")

        return self._impl.getValueUnit(name)

    def setInputDoubleValue(self, name: str, val: float) -> None:
        """(Optional) Provide the code with a scalar double data.

        See Problem documentation for more details on the time semantic of a scalar value.

        Parameters
        ----------
        name : str
            name of the scalar value that is given to the code.
        val : float
            value passed to the code.

        Raises
        ------
        WrongArgument
            exception if the scalar name ('name' parameter) is invalid.
        WrongContext
            exception if called before initialize() or after terminate().
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="setInputDoubleValue",
                               precondition="called before initialize() or after terminate()")
        self._impl.setInputDoubleValue(name=name, val=val)

    def getOutputDoubleValue(self, name: str) -> float:
        """(Optional) Retrieve a scalar double value from the code.

        See Problem documentation for more details on the time semantic of a scalar value.

        Parameters
        ----------
        name : str
            name of the scalar value to be read from the code.

        Returns
        -------
        float
             the double value read from the code.

        Raises
        ------
        WrongArgument
             exception if the scalar name ('name' parameter) is invalid.
        WrongContext
             exception if called before initialize() or after terminate().
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getOutputDoubleValue",
                               precondition="called before initialize() or after terminate()")
        return self._impl.getOutputDoubleValue(name=name)

    def setInputIntValue(self, name: str, val: int) -> None:
        """(Optional) Provide the code with a int data.

        See Problem documentation for more details on the time semantic of a int value.

        Parameters
        ----------
        name : str
            name of the int value that is given to the code.
        val : int
            value passed to the code.

        Raises
        ------
        WrongArgument
            exception if the int name ('name' parameter) is invalid.
        WrongContext
            exception if called before initialize() or after terminate().
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="setInputIntValue",
                               precondition="called before initialize() or after terminate()")
        self._impl.setInputIntValue(name=name, val=val)

    def getOutputIntValue(self, name: str) -> int:
        """(Optional) Retrieve a int value from the code.

        See Problem documentation for more details on the time semantic of a int value.

        Parameters
        ----------
        name : str
            name of the int value to be read from the code.

        Returns
        -------
        int
             the double value read from the code.

        Raises
        ------
        WrongArgument
             exception if the int name ('name' parameter) is invalid.
        WrongContext
             exception if called before initialize() or after terminate().
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getOutputIntValue",
                               precondition="called before initialize() or after terminate()")
        return self._impl.getOutputIntValue(name=name)

    def setInputStringValue(self, name: str, val: str) -> None:
        """(Optional) Provide the code with a string data.

        See Problem documentation for more details on the time semantic of a string value.

        Parameters
        ----------
        name : str
            name of the string value that is given to the code.
        val : str
            value passed to the code.

        Raises
        ------
        WrongArgument
            exception if the string name ('name' parameter) is invalid.
        WrongContext
            exception if called before initialize() or after terminate().
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="setInputStringValue",
                               precondition="called before initialize() or after terminate()")
        self._impl.setInputStringValue(name=name, val=val)

    def getOutputStringValue(self, name: str) -> str:
        """(Optional) Retrieve a string value from the code.

        See Problem documentation for more details on the time semantic of a string value.

        Parameters
        ----------
        name : str
            name of the string value to be read from the code.

        Returns
        -------
        str
             the string value read from the code.

        Raises
        ------
        WrongArgument
             exception if the string name ('name' parameter) is invalid.
        WrongContext
             exception if called before initialize() or after terminate().
        """
        if not self._context:
            raise WrongContext(prob=self._impl.problem_name,
                               method="getOutputStringValue",
                               precondition="called before initialize() or after terminate()")
        return self._impl.getOutputStringValue(name=name)
