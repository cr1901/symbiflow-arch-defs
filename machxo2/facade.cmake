function(facade_setup)
  get_target_property_required(PYTHON3 env PYTHON3)

  set(PYUTILS_PATH "")

  # Vars here mirror the nextpnr equivalents. Their defaults, however, may
  # not match nextpnr/are subject to change.
  set(TRELLIS_PROGRAM_PREFIX "" CACHE STRING "Trellis name prefix")
  if(TRELLIS_PROGRAM_PREFIX)
    message(STATUS "Trellis program prefix: ${TRELLIS_PROGRAM_PREFIX}")
  endif()

  set(TRELLIS_INSTALL_PREFIX ${CMAKE_INSTALL_PREFIX} CACHE STRING "Trellis install prefix")
  message(STATUS "Trellis install prefix: ${TRELLIS_INSTALL_PREFIX}")

  if(NOT DEFINED TRELLIS_LIBDIR)
    if(WIN32)
      set(pytrellis_lib pytrellis.pyd)
    else()
      set(pytrellis_lib pytrellis${CMAKE_SHARED_LIBRARY_SUFFIX})
    endif()

    find_path(TRELLIS_LIBDIR ${pytrellis_lib}
        HINTS ${TRELLIS_INSTALL_PREFIX}/lib/${TRELLIS_PROGRAM_PREFIX}trellis
        PATHS ${CMAKE_SYSTEM_LIBRARY_PATH} ${CMAKE_LIBRARY_PATH}
        PATH_SUFFIXES ${TRELLIS_PROGRAM_PREFIX}trellis
        DOC "Location of the pytrellis library")
    if(NOT TRELLIS_LIBDIR)
        message(FATAL_ERROR "Failed to locate the pytrellis library")
    endif()
  endif()
  message(STATUS "Trellis library directory: ${TRELLIS_LIBDIR}")

  # Analogous to ICESTORM_SHARE
  if(NOT DEFINED TRELLIS_DATADIR)
    set(TRELLIS_DATADIR ${TRELLIS_INSTALL_PREFIX}/share/${TRELLIS_PROGRAM_PREFIX}trellis)
  endif()
  message(STATUS "Trellis data directory: ${TRELLIS_DATADIR}")

  # However, for parity w/ the rest of this repo, binaries must be set
  # manually.
  get_target_property_required(ECPPACK env ECPPACK)
  get_target_property_required(ECPUNPACK env ECPUNPACK)

  set(CELLS_SIM ${YOSYS_DATADIR}/machxo2/cells_sim.v)
  add_file_target(FILE ${CELLS_SIM} ABSOLUTE)

  set(PYPATH_ARG "PYTHONPATH=${TRELLIS_LIBDIR}:${TRELLIS_DATADIR}/util/common:${TRELLIS_DATADIR}/timing/util:${PYUTILS_PATH}")

endfunction()
