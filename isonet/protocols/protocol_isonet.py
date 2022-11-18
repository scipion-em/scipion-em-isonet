# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     J.L. Vilas (jlvilas@cnb.csic.es)
# *
# * your institution
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************


"""
Describe your python module here:
This module will provide the traditional Hello world example
"""
from pyworkflow.protocol import Protocol, params, Integer
from pyworkflow.utils import Message
from pyworkflow.protocol.params import (PointerParam, BooleanParam, FloatParam,
                                        LEVEL_ADVANCED)
import os


TOMOGRAMFOLDER = 'tomo_'

class ProtIsonetProtocol(Protocol):
    """
    This protocol will print hello world in the console
    IMPORTANT: Classes names should be unique, better prefix them
    """
    _label = 'isonet'

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
        Params:
            form: this is the form to be populated with sections and params.
        """

        form.addSection(label='Input')

        form.addParam('inputTomograms', PointerParam, pointerClass='SetOfTomograms',
                      label="Odd tomogram", important=True,
                      help='Select the input tomogram for restoring the missing wedge.')

        form.addParam('useMask', BooleanParam, default=False,
                      label="Use mask?",
                      help='The mask determines which points are specimen'
                           ' and which are not.')

        form.addParam('Mask', PointerParam, pointerClass='VolumeMask',
                      condition='useMask', allowsNull=True,
                      label="Binary Mask",
                      help='The mask determines which points are specimen'
                           ' and which are not')

        form.addParam('ctfDeconv', BooleanParam, default=True,
                      label="Apply CTF deconvolution?",
                      help='Apply CTF deconvolution.')

        group = form.addGroup('Extra parameters')
        line = group.addLine('Resolution Range (Å)',
                             help="Resolution range (and step in expert mode) "
                                  "to analyze the local resolution.")

        group.addParam('significance', FloatParam, default=0.95,
                       expertLevel=LEVEL_ADVANCED,
                       label="Significance",
                       help='Relution is computed using hypothesis tests, '
                            'this value determines the significance of that test')

        line.addParam('minRes', FloatParam, default=0, label='High')
        line.addParam('maxRes', FloatParam, allowsNull=True, label='Low')
        line.addParam('stepSize', FloatParam, allowsNull=True, default=0.5,
                      expertLevel=LEVEL_ADVANCED, label='Step')

        form.addParallelSection(threads=4, mpi=0)

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        # Insert processing steps
        for tomo in self.inputTomograms.get():
            tomId = tomo.getObjId()
            self._insertFunctionStep('prepareProjectStep', tomId)
            if self.ctfDeconv.get():
                self._insertFunctionStep('ctfDeconvolveStep', tomId)
            self._insertFunctionStep('extractSubtomogramsStep')
            self._insertFunctionStep('refineStep')
            self._insertFunctionStep('predictStep')
        self._insertFunctionStep('createOutputStep')

    def prepareProjectStep(self, tomId):
        ts = self.inputTomograms.get()[tomId]
        tsId = ts.getTsId()
        tomoPath = self._getExtraPath(TOMOGRAMFOLDER + tsId)
        os.mkdir(tomoPath)

        #self.runIsonet()

    def ctfDeconvolveStep(self):
        pass

    def extractSubtomogramsStep(self):
        pass

    def refineStep(self):
        pass

    def predictStep(self):
        pass

    def createOutputStep(self):
        # register how many times the message has been printed
        # Now count will be an accumulated value
        timesPrinted = Integer(self.times.get() + self.previousCount.get())
        self._defineOutputs(count=timesPrinted)

    # --------------------------- INFO functions -----------------------------------
    def _summary(self):
        """ Summarize what the protocol has done"""
        summary = []

        if self.isFinished():
            summary.append("This protocol has printed *%s* %i times." % (self.message, self.times))
        return summary

    def _methods(self):
        methods = []

        if self.isFinished():
            methods.append("%s has been printed in this run %i times." % (self.message, self.times))
            if self.previousCount.hasPointer():
                methods.append("Accumulated count from previous runs were %i."
                               " In total, %s messages has been printed."
                               % (self.previousCount, self.count))
        return methods
