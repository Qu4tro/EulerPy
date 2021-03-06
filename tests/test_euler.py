# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import unittest

from click.testing import CliRunner

from EulerPy import euler
from EulerPy.problem import Problem


def EulerRun(*commands, **kwargs):
    """Simplifies running tests using CliRunner()"""
    return CliRunner().invoke(euler.main, commands, **kwargs)


def generateFile(problem, filename=None, correct=False):
    """
    Uses Problem.solution to generate a problem file. The correct
    argument controls whether the generated file is correct or not.
    """
    p = Problem(problem)
    filename = filename or p.filename

    with open(filename, 'a') as file:
        if correct:
            file.write('print({0})\n'.format(p.solution))


class EulerPyTest(unittest.TestCase):
    def setUp(self):
        # Copy problem and solution files to temporary directory
        os.chdir(tempfile.mkdtemp())
        eulerDir = os.path.dirname(os.path.dirname(__file__))
        dataDir = os.path.join(eulerDir, 'EulerPy', 'data')
        tempData = os.path.join(os.getcwd(), 'EulerPy', 'data')
        shutil.copytree(dataDir, tempData)

    def tearDown(self):
        # Delete the temporary directory
        shutil.rmtree(os.getcwd())


class EulerPyNoOption(EulerPyTest):
    # Empty directory with no option
    def test_empty_directory_install_neutral(self):
        result = EulerRun(input='\n')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isfile('001.py'))

    def test_empty_directory_negative(self):
        result = EulerRun(input='N\n')
        self.assertEqual(result.exit_code, 1)
        self.assertFalse(os.path.isfile('001.py'))

    # No option or problem number; should verify and generate next file
    def test_no_arguments(self):
        generateFile(1, correct=True)
        result = EulerRun(input='\n')
        self.assertEqual(result.exit_code, 0)

    # Ambiguous case; infer option from file existence check
    def test_ambiguous_option_generate(self):
        result = EulerRun('1')
        self.assertEqual(result.exit_code, 0)

    def test_ambiguous_option_verify(self):
        generateFile(1, correct=True)
        result = EulerRun('1')
        self.assertEqual(result.exit_code, 0)


class EulerPyCheat(EulerPyTest):
    def test_cheat_neutral(self):
        result = EulerRun('-c', input='\n')
        self.assertEqual(result.exit_code, 1)

    def test_cheat_long_flag(self):
        result = EulerRun('--cheat', input='\n')
        self.assertEqual(result.exit_code, 1)

    def test_cheat_positive(self):
        result = EulerRun('-c', input='Y\n')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('The answer to problem 1' in result.output)

    def test_chest_specific(self):
        result = EulerRun('-c', '2', input='Y\n')
        self.assertTrue('The answer to problem 2' in result.output)

    def test_cheat_not_in_solutions(self):
        result = EulerRun('-c', '1000', input='Y\n')
        self.assertEqual(result.exit_code, 1)


class EulerPyGenerate(EulerPyTest):
    def test_generate_neutral(self):
        result = EulerRun('-g', input='\n')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isfile('001.py'))

    def test_generate_negative(self):
        result = EulerRun('-g', input='N\n')
        self.assertEqual(result.exit_code, 1)
        self.assertFalse(os.path.isfile('001.py'))

    def test_generate_specific(self):
        result = EulerRun('-g', '5', input='\n')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isfile('005.py'))

    def test_generate_overwrite_positive(self):
        generateFile(1)

        result = EulerRun('-g', '1', input='\nY\n')
        self.assertEqual(result.exit_code, 0)

        with open('001.py') as file:
            self.assertFalse(file.readlines() == [])

    def test_generate_overwrite_neutral(self):
        generateFile(1)

        result = EulerRun('-g', '1', input='\n\n')
        self.assertEqual(result.exit_code, 1)

        with open('001.py') as file:
            self.assertTrue(file.readlines() == [])

    def test_generate_overwrite_skipped(self):
        generateFile(1, '001-skipped.py')

        result = EulerRun('-g', '1', input='\nY\n')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isfile('001-skipped.py'))
        self.assertFalse(os.path.isfile('001.py'))

    def test_generate_copy_resources(self):
        result = EulerRun('-g', '22', input='\n')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.isfile('022.py'))

        resource = os.path.join('resources', 'names.txt')
        self.assertTrue(os.path.isfile(resource))


class EulerPyPreview(EulerPyTest):
    def test_preview(self):
        result = EulerRun('-p')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('Project Euler Problem 1' in result.output)

    def test_preview_specific(self):
        result = EulerRun('-p', '5')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('Project Euler Problem 5' in result.output)

    def test_preview_next_behaviour(self):
        generateFile(1)

        result = EulerRun('-p')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('Project Euler Problem 2' in result.output)

    def test_preview_nonexistent(self):
        result = EulerRun('-p', '1000')
        self.assertEqual(result.exit_code, 1)


class EulerPySkip(EulerPyTest):
    def test_skip_neutral(self):
        generateFile(1)

        result = EulerRun('-s', input='\n')
        self.assertEqual(result.exit_code, 1)
        self.assertTrue(os.path.isfile('001.py'))

    def test_skip_positive(self):
        generateFile(1)

        result = EulerRun('-s', input='Y\n')
        self.assertEqual(result.exit_code, 0)
        self.assertFalse(os.path.isfile('001.py'))
        self.assertTrue(os.path.isfile('001-skipped.py'))


class EulerPyVerify(EulerPyTest):
    def test_verify(self):
        generateFile(1)

        result = EulerRun('-v')
        self.assertEqual(result.exit_code, 1)
        self.assertTrue('Checking "001.py"' in result.output)

    def test_verify_specific(self):
        generateFile(5)

        result = EulerRun('-v', '5')
        self.assertEqual(result.exit_code, 1)
        self.assertTrue('Checking "005.py"' in result.output)

    def test_verify_glob(self):
        generateFile(1, '001-skipped.py')

        result = EulerRun('-v', '1')
        self.assertEqual(result.exit_code, 1)
        self.assertTrue('Checking "001-skipped.py"' in result.output)

    def test_verify_sorted_glob(self):
        generateFile(1, '001.py')
        generateFile(1, '001-skipped.py')

        result = EulerRun('-v', '1')
        self.assertEqual(result.exit_code, 1)
        self.assertTrue('Checking "001.py"' in result.output)
        self.assertFalse('Checking "001-skipped.py"' in result.output)

    def test_verify_correct(self):
        generateFile(1, correct=True)

        result = EulerRun('-v')
        self.assertEqual(result.exit_code, 0)

    def test_verify_non_existent_problem_file(self):
        result = EulerRun('-v', '5')
        self.assertEqual(result.exit_code, 1)

    def test_verify_file_with_multiline_output(self):
        with open('001.py', 'a') as file:
            file.write('print(1); print(2)')

        result = EulerRun('-v', '1')
        self.assertEqual(result.exit_code, 1)

    def test_verify_error_file(self):
        with open('001.py', 'a') as file:
            file.write('import sys; sys.exit(1)')

        result = EulerRun('-v', '1')
        self.assertTrue('Error calling "001.py"' in result.output)
        self.assertEqual(result.exit_code, 1)


class EulerPyVerifyAll(EulerPyTest):
    def test_verify_all(self):
        generateFile(1, correct=True)
        generateFile(2, filename='002-skipped.py', correct=True)
        generateFile(4)

        with open('005.py', 'a') as file:
            file.write('import sys; sys.exit(1)')

        result = EulerRun('--verify-all')
        self.assertTrue('Problems 001-020: C C . I E' in result.output)

        # "002-skipped.py" should have been renamed to "002.py"
        self.assertTrue(os.path.isfile('002.py'))
        self.assertFalse(os.path.isfile('002-skipped.py'))

        # "004.py" should have been renamed to "004-skipped.py"
        self.assertFalse(os.path.isfile('004.py'))
        self.assertTrue(os.path.isfile('004-skipped.py'))

    def test_verify_all_no_files(self):
        result = EulerRun('--verify-all')
        self.assertEqual(result.exit_code, 1)


class EulerPyMisc(EulerPyTest):
    def test_help_option(self):
        result = EulerRun('--help')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('--cheat' in result.output)
        self.assertTrue('--generate' in result.output)
        self.assertTrue('--preview' in result.output)
        self.assertTrue('--skip' in result.output)
        self.assertTrue('--verify' in result.output)
        self.assertTrue('--verify-all' in result.output)

    def test_version_option(self):
        result = EulerRun('--version')
        self.assertEqual(result.exit_code, 0)

