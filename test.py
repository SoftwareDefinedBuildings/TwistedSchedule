import unittest
from twistedschedule import cron

class TestCronScheduleGeneration(unittest.TestCase):
    def setUp(self):
        self.seq = cron.CronSchedule._seq
        self.step = cron.CronSchedule._step
        self.seq_samples = [
         ('1,3,5-10', [1,3,5,6,7,8,9,10]),
         ('1,3,5', [1,3,5]),
         ('1-5', [1,2,3,4,5]),
         ('1-5,10-12',[1,2,3,4,5,10,11,12]),
         ('1-5,7,8',[1,2,3,4,5,7,8]),
        ]
        self.step_samples = [
            (('minute', '*/10'), [0,10,20,30,40,50]),
            (('hour', '*/4'), [0,4,8,12,16,20]),
            (('day_of_week', '*/3'), [0,3,6]),
            (('second', '*/50'), [0,50]),
        ]
        self.invalids = [
            '1.3,2.4',
            '*/5.5',
            'asdsf',
            '1,3,5.10',
        ]

    def testPositiveSeqMatches(self):
        for sample in self.seq_samples:
            match = self.seq.match(sample[0])
            self.assertIsNotNone(match)
            self.assertEqual(match.group(), sample[0])
    
    def testSequenceExpansion(self):
        cs = cron.CronSchedule(second='1')
        for sample in self.seq_samples:
            self.assertEqual(cs._expand_sequence(sample[0]), sample[1])

    def testPositiveStepMatches(self):
        for sample in self.step_samples:
            match = self.step.match(sample[0][1])
            self.assertIsNotNone(match)
            self.assertEqual(match.group(),sample[0][1])

    def testStepExpansion(self):
        cs = cron.CronSchedule(second='1')
        for sample in self.step_samples:
            self.assertEqual(cs._expand_step(sample[0][0],sample[0][1]), sample[1])

    def testInvalidChars(self):
        cs = cron.CronSchedule(second='1')
        for invalid in self.invalids:
            self.assertFalse(cs._is_valid_chars(invalid))

        for valid in self.seq_samples:
            self.assertTrue(cs._is_valid_chars(valid[0]))

if __name__ == '__main__':
    unittest.main()
