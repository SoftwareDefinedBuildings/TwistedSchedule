import unittest
import cron

class TestRegex(unittest.TestCase):
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
            ({'minute': '*/10'}, [0,10,20,30,40,50]),
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

    def testPositiveEveryMatches(self):
        match = self.step.match('*/5')
        self.assertIsNotNone(match)
        self.assertEqual(match.group(), '*/5')

        match = self.step.match('*/55')
        self.assertIsNotNone(match)
        self.assertEqual(match.group(), '*/55')

    def testStepExpansion(self):
        pass

if __name__ == '__main__':
    unittest.main()
