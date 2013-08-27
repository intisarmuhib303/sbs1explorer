#    Copyright (C) 2008 Vasco Costa <vasco dot costa at geekslot dot com>
#
#    This file is part of sbs1explorer.
#
#    sbs1explorer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    sbs1explorer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.


"""Business layer of the application.

This module through the use of the mbiz module independently implements all the
business logic of the application leveraging the complete separation between
the presentation layer and the business layer.

All the classes are derived from the base ones found on the mbiz module.

Classes:

Aircraft - class representing aircraft objects.
AircraftController - class representing business rules.

Exceptions:

DatabaseError - exception representing database errors.

"""

import os
import sys

import mbiz


class Aircraft(mbiz.Model):

    """Aircraft model derived from Model."""

    def __init__(self, database_path):
        """Initialize the Aircraft model by calling the __init__ method of the parent class."""
        mbiz.Model.__init__(self, database_path, child='FLights', primary_key='aircraftid', foreign_key='aircraftid')


class AircraftController(mbiz.Controller):

    """AircraftController controller derived from Controller."""

    def __init__(self, database_path):
        """Initialize the AircraftController controller by calling the __init__ method of the parent class."""
        mbiz.Controller.__init__(self, Aircraft(database_path))

    def search(self, data):
        """Search the Aircraft model for the given data."""
        fields = ('starttime',
                  'firstsquawk',
                  'callsign',
                  'hadalert',
                  'hademergency',
                  'hadspi', 'modes',
                  'registration',
                  'icaotypecode',
                  'operatorflagcode',
                  'modescountry')
        criteria = {}
        for key in data:
            if data[key] != '':
                criteria[key] = data[key]
        if len(criteria) == 0:
            criteria = None
        try:
            self.model.find(fields, criteria)
        except mbiz.DatabaseError, e:
            raise DatabaseError(e.message)
        self.set(self, 'results', self.model)

    def browser_lookup(self, data):
        """Lookup in a browser further details for the given data."""
        if data.has_key('callsign'):
            airline = ''
            for character in data['callsign']:
                if character.isdigit():
                    break
                airline += character
            flight = data['callsign'][len(airline):]
            if sys.platform == 'linux2':
                os.system('firefox www.flightstats.com/go/FlightStatus/flightStatusByFlight.do?airline=' + airline + '\&flightNumber=' + flight)
            if sys.platform == 'win32':
                os.system('start iexplore "www.flightstats.com/go/FlightStatus/flightStatusByFlight.do?airline=' + airline + '&flightNumber=' + flight + '"')
        if data.has_key('registration'):
            if sys.platform == 'linux2':
                os.system('firefox www.airframes.org/reg/' + data['registration'].replace('-', ''))
            if sys.platform == 'win32':
                os.system('start iexplore "www.airframes.org/reg/' + data['registration'].replace('-', '') + '"')


class DatabaseError(Exception):

    """Class representing a database error."""

    def __init__(self, message):
        """Initialize the exception by setting its message attribute."""
        self.message = message

    def __str___(self):
        """Return the string representation of the exception."""
        return repr(self.message)
