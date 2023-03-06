# **************************************************************************
# *
# * Authors: Yunior C. Fonseca Reyna    (cfonseca@cnb.csic.es)
# *
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
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


def getIsoNetEnvName(version):
    return 'isonet-%s' % version


def getTrinedModelName(iter):
    model = 'model_iter%s.h5' % iter
    if iter < 10:
        model = 'model_iter0%s.h5' % iter
    return model

# IsoNet environment variables
ISONET_VERSION = '0.2.1'  # This is our made up version
ISONET_ACTIVATION_CMD = 'conda activate %s' % (getIsoNetEnvName(ISONET_VERSION))

ISONET_CUDA_LIB = 'ISONET_CUDA_LIB'
ISONET_HOME = 'ISONET_HOME'

# IsoNet programs
ISONET_SCRIPT = 'isonet.py'
PROGRAM_PREPARE_STAR = 'prepare_star'
PROGRAM_CTF_DECONV = 'deconv'
PROGRAM_GENERATE_MASK = 'make_mask'
PROGRAM_EXTRACT_SUBTOMOGRAMS = 'extract'
PROGRAM_REFINE = 'refine'
PROGRAM_PREDICT = 'predict'

NOISE_MODE = ['ramp', 'hamming', 'noFilter']

TOMOGRAMFOLDER = 'tomograms'
DECONVFOLDER = 'deconv'
SUBTOMOGRAMFOLDER = 'subtomograms'
RESULTFOLDER = 'results'
MASKFOLDER = 'mask'
PREDICTEDFOLDER = 'predicted'

OUTPUT_TOMO_STAR_FILE = 'tomograms.star'
OUTPUT_TOMO_DECONV_STAR_FILE = 'tomograms_new.star'
OUTPUT_SUBTOMO_STAR_FILE = 'subtomograms.star'
