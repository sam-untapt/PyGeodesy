
# -*- coding: utf-8 -*-

# Python implementation of geodesy tools for an ellipsoidal earth model.
# Transcribed from JavaScript originals by (C) Chris Veness 2005-2016
# and published under the same MIT Licence**, see for example
# <http://www.movable-type.co.uk/scripts/LatLongVincenty.html>,
# <http://github.com/geopy> and <http://python.org/pypi/geopy>.

# Calculate geodesic distance between two points using the Vincenty
# methods <https://en.wikipedia.org/wiki/Vincenty's_formulae> and
# one of several ellipsoid models of the earth.  The default model is
# WGS-84, most accurate and widely used globally-applicable model for
# the earth ellipsoid.
#
# Other ellipsoids offering a better fit to the local geoid include
# Airy (1830) in the UK, Clarke (1880) in Africa, International 1924
# in much of Europe, and GRS-67 in South America.  North America
# (NAD83) and Australia (GDA) use GRS-80, which is equivalent to the
# WGS-84 model.
#
# Great-circle distance uses a spherical model of the earth with the
# mean earth radius defined by the International Union of Geodesy and
# Geophysics (IUGG) as (2 * a + b) / 3 = 6371008.7714150598 meter or
# approx. 6371009 meter (for WGS-84, resulting in an error of up to
# about 0.5%).
#
# Here's an example usage of Vincenty:
#
#     >>> from geodesy.ellipsoidalVincenty import LatLon
#     >>> Newport_RI = LatLon(41.49008, -71.312796)
#     >>> Cleveland_OH = LatLon(41.499498, -81.695391)
#     >>> print(Newport_RI.distanceTo(Cleveland_OH))
#     866455.432916  # meter
#
# You can change the ellipsoid model used by the Vincenty formulae
# as follows:
#
#     >>> from geodesy import Datums
#     >>> from geodesy.ellipsoidalVincenty import LatLon
#     >>> p = LatLon(0, 0, datum=Datums.OSGB36)
#
# or by converting to anothor datum:
#
#     >>> p = p.convertDatum(Datums.OSGB36)

from datum import Datums
from ellipsoidalBase import _CartesianBase, _LatLonHeightDatumBase
from utils import EPS, degrees90, degrees180, degrees360, radians
from math import atan2, cos, hypot, sin, tan

# all public contants, classes and functions
__all__ = ('Cartesian', 'LatLon', 'VincentyError')  # classes
__version__ = '17.02.01'


class VincentyError(Exception):
    '''Error thrown from Vincenty's direct and inverse methods
       for coincident points and lack of convergence.
    '''
    pass


class Cartesian(_CartesianBase):
    '''Extend with method to convert Cartesian to
       Vincenty-based LatLon.
    '''
    def toLatLon(self, datum=Datums.WGS84):  # PYCHOK XXX
        '''Converts this (geocentric) Cartesian (x/y/z) point to
           (ellipsoidal geodetic) LatLon point on the specified datum.

           @param {Datum} [datum=Datums.WGS84] - Datum to use.

           @returns {LatLon} The (ellipsoidal) LatLon point.
        '''
        a, b, h = self.to3llh(datum)
        return LatLon(a, b, height=h, datum=datum)  # Vincenty


class LatLon(_LatLonHeightDatumBase):
    '''Using the formulae devised by Thaddeus Vincenty (1975) with an
       ellipsoidal model of the earth to compute the geodesic distance
       and bearings between two given points or the destination point
       given an start point and initial bearing.

       Set the earth model to be used with the keyword argument
       datum.  The default is Datums.WGS84, which is the most globally
       accurate.  For other models, see the Datums in module datum.

       Note: This implementation of the Vincenty methods may not
       converge for some valid points, raising a VincentyError.  In
       that case, a result may be obtained by increasing the epsilon
       and/or the iteration limit, see LatLon properties epsilon and
       iterations.
    '''
    _epsilon    = 1.0e-12  # about 0.006 mm
    _iterations = 50

    def copy(self):
        '''Return a copy of this point.

           @returns {LatLon} Copy of this point.
        '''
        p = _LatLonHeightDatumBase.copy(self)
        assert hasattr(p, 'epsilon')
        p.epsilon = self.epsilon
        assert hasattr(p, 'iterations')
        p.iterations = self.iterations
        return p

    def destination(self, distance, bearing):
        '''Return the destination point after having travelled
           for the given distance from this point along a geodesic
           given by an initial bearing, using Vincenty's direct
           method.

           See method destination2 for more details, parameter
           descriptions and exceptions thrown.

           @returns {LatLon} The destination point.

           @example
           p = LatLon(-37.95103, 144.42487);
           d = p.destination(54972.271, 306.86816)  # 37.6528°S, 143.9265°E
        '''
        return self._direct(distance, bearing, True)[0]

    def destination2(self, distance, bearing):
        '''Return the destination point and the final bearing (reverse
           azimuth) after having travelled for the given distance from
           this point along a geodesic given by an initial bearing,
           using Vincenty's direct method.

           The distance must be in the same units as this point's datum
           axes, conventially meter.  The distance is measured on the
           surface of the ellipsoid, ignoring this point's height.

           The initial and final bearing (aka forward and reverse azimuth)
           are in compass degrees from North.

           The destination point's height and datum are set to this
           point's height and datum.

           @param {number} distance - Distance in meters.
           @param {degrees} bearing - Initial bearing in degrees from North.

           @returns {(LatLon, degrees360)} 2-Tuple of (destination point,
                                           final bearing), with the latter
                                           in degrees from North.

           @throws {VincentyError} If Vincenty failed to converge for the
                                   current epsilon and iteration limit.

           @example
           p = LatLon(-37.95103, 144.42487)
           b = 306.86816
           d, f = p.destination2(54972.271, b)  # 37.652818°S, 143.926498°E, 307.1736
        '''
        return self._direct(distance, bearing, True)

    def distanceTo(self, other):
        '''Compute the distance between this and an other point
           along a geodesic, using Vincenty's inverse method.

           See method distanceTo3 for more details, parameter
           descriptions and exceptions thrown.

           @returns {number} Distance in meters.

           @example
           p = LatLon(50.06632, -5.71475)
           q = LatLon(58.64402, -3.07009)
           d = p.distanceTo(q)  # 969,954.166 m
        '''
        return self._inverse(other, False)

    def distanceTo3(self, other):
        '''Compute the distance and the initial and final bearing along
           a geodesic between this and an other point, using Vincenty's
           inverse method.

           The distance is in the same units as this point's datum axes,
           conventially meter.  The distance is measured on the surface
           of the ellipsoid, ignoring this point's height.

           The initial and final bearing (aka forward and reverse azimuth)
           are in compass degrees from North.

           @param {LatLon} other - Destination LatLon point.

           @returns {(meter, degrees360, degrees360)} 3-Tuple with
                       (distance, initial bearing, final bearing).

           @throws {TypeError} If this and the other point's LatLon
                               types are incompatiple.
           @throws {ValueError} If this and the other point's datum
                                ellipsoids do not match.
           @throws {VincentyError} If Vincenty failed to converge for
                                   the current epsilon and iteration
                                   limit or if both points coincide.
        '''
        return self._inverse(other, True)

    @property
    def epsilon(self, eps=None):
        '''Get the convergence epsilon.
        '''
        return self._epsilon

    @epsilon.setter  # PYCHOK setter!
    def epsilon(self, eps):
        '''Set the convergence epsilon.

           @param {float} eps - New epsilon value.
        '''
        if 0 < float(eps) < 1:
            self._epsilon = float(eps)

    def finalBearingOn(self, distance, bearing):
        '''Return the final bearing (reverse azimuth) after having
           travelled for the given distance along a geodesic given
           by an initial bearing from this point, using Vincenty's
           direct method.

           See method destination2 for more details, parameter
           descriptions and exceptions thrown.

           @returns {degrees360} Final bearing in degrees from North.

           @example
           p = LatLon(-37.95103, 144.42487)
           b = 306.86816
           f = p.finalBearingOn(54972.271, b)  # 307.1736
        '''
        return self._direct(distance, bearing, False)

    def finalBearingTo(self, other):
        '''Return the final bearing (reverse azimuth) after having
           travelled along a geodesic from this point to an other
           point, using Vincenty's inverse method.

           See method distanceTo3 for more details, parameter
           descriptions and exceptions thrown.

           @returns {degrees360} Final bearing in degrees from North.

           @example
           p = new LatLon(50.06632, -5.71475)
           q = new LatLon(58.64402, -3.07009)
           f = p1.finalBearingTo(q)  # 11.2972°

           p = LatLon(52.205, 0.119)
           q = LatLon(48.857, 2.351)
           f = p.finalBearingTo(q)  # 157.9
        '''
        return self._inverse(other, True)[2]

    def initialBearingTo(self, other):
        '''Return the initial bearing (forward azimuth) to travel
           along a geodesic fromfrom this point to an other point,
           using Vincenty's inverse method.

           See method distanceTo3 for more details, parameter
           descriptions and exceptions thrown.

           @returns {degrees360} Initial bearing in degrees from North.

           @example
           p = LatLon(50.06632, -5.71475)
           q = LatLon(58.64402, -3.07009)
           b = p.bearingTo(q)  # 9.1419°

           p = LatLon(52.205, 0.119)
           q = LatLon(48.857, 2.351)
           b = p.bearingTo(q)  # 156.2°
        '''
        return self._inverse(other, True)[1]

    bearingTo = initialBearingTo  # XXX original name

    @property
    def iterations(self):
        '''Get the limit for the number of iterations.
        '''
        return self._iterations

    @iterations.setter  # PYCHOK setter!
    def iterations(self, limit):
        '''Set the limit for the number of iterations.

           @param {number} limit - New iteration limit.
        '''
        if 2 < int(limit) < 200:
            self._iterations = int(limit)

    def toCartesian(self):
        '''Convert this (geodetic) LatLon point to (geocentric) x/y/z
           cartesian coordinates.

           @returns {Cartesian} Cartesian point equivalent, with x,
                                y and z in meter from earth center.
        '''
        x, y, z = self.to3xyz()  # ellipsoidalBase._LatLonHeightDatumBase
        return Cartesian(x, y, z)  # this ellipsoidalVincenty.Cartesian

    def _direct(self, distance, bearing, llr):
        # direct Vincenty method, private
        E = self.ellipsoid()

        c1, s1, t1 = _r3(self.lat, E.f)

        i = radians(bearing)  # initial bearing, forward azimuth
        ci, si = cos(i), sin(i)
        s12 = atan2(t1, ci) * 2

        sa = c1 * si
        c2a = 1 - (sa * sa)
        if c2a < EPS:
            c2a = 0
            A, B = 1, 0
        else:  # e22 == (a / b) ^ 2 - 1
            A, B = _p2(c2a, E.e22)

        s = d = distance / (E.b * A)
        for _ in range(self._iterations):
            cs, ss, c2sm = cos(s), sin(s), cos(s12 + s)
            s_, s = s, d + _ds(B, cs, ss, c2sm)
            if abs(s - s_) < self._epsilon:
                break
        else:
            raise VincentyError('no convergence %r' % (self,))

        t = s1 * ss - c1 * cs * ci
        # reverse azimuth (final bearing) in [0, 360)
        r = degrees360(atan2(sa, -t))
        if llr:
            # destination latitude in [-90, 90)
            a = degrees90(atan2(s1 * cs + c1 * ss * ci,
                                (1 - E.f) * hypot(sa, t)))
            # destination longitude in [-180, 180)
            b = degrees180(atan2(ss * si, c1 * cs - s1 * ss * ci) -
                          _dl(E.f, c2a, sa, s, cs, ss, c2sm) +
                           radians(self.lon))
            r = LatLon(a, b, height=self.height, datum=self.datum), r
        return r

    def _inverse(self, other, azis):
        # inverse Vincenty method, private
        E = self.ellipsoids(other)

        c1, s1, _ = _r3(self.lat, E.f)
        c2, s2, _ = _r3(other.lat, E.f)

        c1c2, s1s2 = c1 * c2, s1 * s2
        c1s2, s1c2 = c1 * s2, s1 * c2

        ll = dl = radians(abs(other.lon - self.lon))
        for _ in range(self._iterations):
            cll, sll, ll_ = cos(ll), sin(ll), ll

            t2 = c2 * sll, c1s2 - s1c2 * cll
            ss = hypot(*t2)
            if ss < EPS:
                raise VincentyError('%r coincident with %r' % (self, other))
            cs = s1s2 + c1c2 * cll
            s = atan2(ss, cs)

            sa = c1c2 * sll / ss
            c2a = 1 - (sa * sa)
            if abs(c2a) < EPS:
                c2a = 0  # equatorial line
                ll = dl + E.f * sa * s
            else:
                c2sm = cs - 2 * s1s2 / c2a
                ll = dl + _dl(E.f, c2a, sa, s, cs, ss, c2sm)

            if abs(ll - ll_) < self._epsilon:
                break
        else:
            raise VincentyError('no convergence %r to %r' % (self, other))

        if c2a:  # e22 == (a / b) ^ 2 - 1
            A, B = _p2(c2a, E.e22)
            s = A * (s - _ds(B, cs, ss, c2sm))

        b = E.b
#       if self.height or other.height:
#           b += self._alter(other)
        d = b * s

        if azis:  # forward and reverse azimuth
            f = degrees360(atan2(*t2))
            r = degrees360(atan2(c1 * sll, -s1c2 + c1s2 * cll))
            d = d, f, r
        return d


def _p2(c2a, ab2):  # A, B polynomials
    u2 = c2a * ab2  # e'2 WGS84 = 0.00673949674227643
    A = u2 / 16384.0 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2))) + 1
    B = u2 /  1024.0 * ( 256 + u2 * (-128 + u2 * ( 74 -  47 * u2)))
    return A, B


def _r3(a, f):  # reduced cos, sin, tan
    t = (1 - f) * tan(radians(a))
    c = 1 / hypot(1, t)
    s = t * c
    return c, s, t


def _dl(f, c2a, sa, s, cs, ss, c2sm):
    C = f / 16.0 * c2a * (4 + f * (4 - 3 * c2a))
    return (1 - C) * f * sa * (s + C * ss * (c2sm +
                     C * cs * (c2sm * c2sm * 2 - 1)))


def _ds(B, cs, ss, c2sm):
    c2sm2 = 2 * c2sm * c2sm - 1
    ss2 = (ss * ss * 4 - 3) * (c2sm2 * 2 - 1)
    return B * ss * (c2sm + B / 4.0 * (c2sm2 * cs -
                            B / 6.0 *  c2sm  * ss2))

# **) MIT License
#
# Copyright (C) 2016-2017 -- mrJean1@Gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
