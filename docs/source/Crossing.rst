:orphan:

Crossing Explanation
====================

In both examples the level crossing is triggered automatically by the train going over sensors.
This was not achieved with Python but instead with EX-RAIL on board the DCC-EX command station.
To help people understand the examples this page documents that part of the project.

First, we define aliases between the pin number on the Arduino and a human friendly name.
.. code-block::

    TURNOUTL(1001, 1, "Station CCW")
    TURNOUTL(1002, 2, "Mainline Select Front")
    TURNOUTL(1003, 3, "Tram Station")
    TURNOUTL(1004, 4, "Station CW")
    TURNOUTL(1005, 5, "Mainline Select Back")

    // train roster omitted.

    ALIAS(crossing, 52)

    ALIAS(crossingCCW, 49)
    ALIAS(stationCW, 47)
    ALIAS(main1CW, 45)
    ALIAS(main2CW, 43)

Note that "crossing" is the output to turn the crossing on or off, the others are all infrared sensors under the track.
The name denotes the direction the train is traveling, either clockwise (CW) or counter-clockwise (CCW).

To avoid the signals running when a train is stopped in one of the sidings, logic is used to check turnout state and sensor state so the signal will only run when a train is approaching the crossing, and switches are set that the train can travel over the crossing.
.. code-block::

    AUTOSTART SEQUENCE(1)
        DELAY(50)
        IF(crossingCCW)
            LATCH(100)
            FOLLOW(1)
        ENDIF
        IF(stationCW)
            IFTHROWN(1001)
                LATCH(100)
                FOLLOW(1)
            ENDIF
        ENDIF
        IF(main1CW)
            IFCLOSED(1001)
                IFCLOSED(1002)
                    LATCH(100)
                    FOLLOW(1)
                ENDIF
            ENDIF
        ENDIF
        IF(main2CW)
            IFCLOSED(1001)
                IFTHROWN(1002)
                    LATCH(100)
                    FOLLOW(1)
                ENDIF
            ENDIF
        ENDIF

    UNLATCH(100)
    FOLLOW(1)

This also uses a virtual pin (100) which is later sent to the real pin in a different sequence.
.. code-block::

    AUTOSTART SEQUENCE(2)
        AT(100)
        SET(crossing)
        AFTER(100)
        DELAY(6000)
        IFNOT(100)
            RESET(crossing)
        ENDIF
        FOLLOW(2)

The delay here allows a train to clear the crossing even if the sensor has since been cleared.

Further information on EX-RAIL can be found in DCC-EX's official documentation.