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


"""Minimalist MVC framework implementing the business layer.

This module aims to provide a minimalist framework for simple applications
using the MVC (Model View Controller) architectural pattern.

The amount of classes and methods provided is intentionally kept to a minimum,
so that a good balance between functionality and complexity is achieved. Though
basic code for database abstraction is included don't expect a full blown
framework, there are already lots of good ones available. The author of this
code sees software minimalism as the way to go for the average project since
unneeded complexity tends to make your programs more error prone. On top of
that this framework came to life as a way to easily produce simple MVC projects
which would otherwise be complicated by the available frameworks.

This framework also intends to be used both for web and standalone applications
so that there's only one simple API to learn as fast as possible, whereas other
libraries usually require a medium to steep learning curve. The API should be
basic enough so that you can learn it in less than 24 hours avoiding loosing
time at the beggining but still have a bare set of tools which leverage your
application. This obviously comes at a cost, you'll have to produce more code
by your self, hopefully better one since you fully understand the framework.

You should derive from the classes in this module to get basic funcionality and
extend them as needed. Feel free to send me your extensions if you think the
balance between a simple framework and functionality could be improved.

Currently only sqlite databases are supported since it's still a beta project
but all major databases will be available in the near future.

Classes:

Model - class representing data objects.
Controller - class representing business rules.

Exceptions:

DatabaseError - exception representing database errors.

"""

import os
import sqlite3

import config


class Model(list):

    """Base class for models."""

    def __init__(self, database_path=config.DATABASE_PATH, name=None, child=None, primary_key=None, foreign_key=None, join=config.JOIN):
        """Initialize the model by connecting to the database and setting sane default values for its attributes."""
        self.connection = sqlite3.connect(database_path)
        self.cursor = self.connection.cursor()
        if name != None:
            self.name = name
        else:
            self.name = self.__class__.__name__
        if child != None:
            self.child = child
        else:
            self.child = None
        if primary_key != None:
            self.primary_key = primary_key
        else:
            self.primary_key = "id"
        if foreign_key != None:
            self.foreign_key = foreign_key
        else:
            self.foreign_key = self.name + "_id"
        self.join = join

    def read(self, id):
        """Read a single record from the table corresponding to this model."""
        sql_statement = "SELECT * FROM " + self.name + " WHERE " + self.primary_key + " = " + str(id)
        if config.DEBUG:
            print sql_statement
        try:
            self.cursor.execute(sql_statement)
        except (sqlite3.OperationalError, sqlite3.DatabaseError), e:
            raise DatabaseError(e.message)
        if len(self) != 0:
            del self[:]
        for row in self.cursor:
            self.append(row)

    def write(self, data):
        """Write a single record to the table corresponding to this model."""
        sql_statement = "INSERT INTO " + self.name + " (" + self.primary_key + ", " + ", ".join(data.keys()) + ") " +\
                        "VALUES(NULL, '" + "', '".join(data.values()) + "')"
        if config.DEBUG:
            print sql_statement 
        try:
            self.cursor.execute(sql_statement)
            self.connection.commit()
        except (sqlite3.OperationalError, sqlite3.DatabaseError), e:
            raise DatabaseError(e.message)

    def delete(self, id):
        """Delete a single record from the table corresponding to this model."""
        sql_statement = "DELETE FROM " + self.name + " WHERE " + self.primary_key + " = " + str(id)
        if config.DEBUG:
            print sql_statement
        try:
            self.cursor.execute(sql_statement)
            self.connection.commit()
        except (sqlite3.OperationalError, sqlite3.DatabaseError), e:
            raise DatabaseError(e.message)

    def find(self, fields=None, criteria=None, limit=config.LIMIT):
        """Find a record set from the table(s) corresponding to this model according to the given fields, criteria and limit."""
        sql_statement = "SELECT "
        if fields != None:
            for field in fields:
                sql_statement += field
                if field != fields[-1]:
                    sql_statement += ", "
        else:
            sql_statement += "*"
        sql_statement += " FROM " + self.name
        if self.child != None:
            sql_statement += " " + self.join + " " + self.child + " ON " +\
                                   self.name + "." + self.primary_key + " = " + self.child + "." + self.foreign_key
        if criteria != None:
            sql_statement += " WHERE "
            for constrain in criteria.keys():
                if criteria[constrain].find("%") != -1 or criteria[constrain].find("_") != -1:
                    sql_statement += constrain + " LIKE :" + constrain
                else:
                    sql_statement += constrain + " = :" + constrain
                if constrain != criteria.keys()[-1]:
                    sql_statement += " AND "
            sql_statement += " LIMIT " + str(limit)
            try:
                self.cursor.execute(sql_statement, criteria)
            except (sqlite3.OperationalError, sqlite3.DatabaseError), e:
                raise DatabaseError(e.message)
        else:
            sql_statement += " LIMIT " + str(limit)
            try:
                self.cursor.execute(sql_statement)
            except (sqlite3.OperationalError, sqlite3.DatabaseError), e:
                raise DatabaseError(e.message)
        if config.DEBUG:
            print sql_statement
        if len(self) != 0:
            del self[:]
        for row in self.cursor:
            self.append(row)

    def raw_sql(self, sql_statement):
        """Execute a raw sql statement."""
        try:
            self.cursor.execute(sql_statement)
        except (sqlite3.OperationalError, sqlite3.DatabaseError), e:
            raise DatabaseError(e.message)
        if len(self) != 0:
            del self[:]
        for row in self.cursor:
            self.append(row)


class Controller:

    """Base class for controllers."""
    
    def __init__(self, model):
        """Initialize the controller by setting its module attribute."""
        self.model = model

    def set(self, object, attribute, value):
        """Set the given attribute of a given object to the given value."""
        setattr(object, attribute, value)


class DatabaseError(Exception):

    """Class representing a database error."""

    def __init__(self, message):
        """Initialize the exception by setting its message attribute."""
        self.message = message

    def __str___(self):
        """Rerturn the string representation of the exception."""
        return repr(self.message)
