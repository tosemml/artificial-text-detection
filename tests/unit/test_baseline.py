import argparse
import numpy as np
import os
import shutil
import torch

from hamcrest import assert_that, equal_to
from unittest import TestCase

from transformers import EvalPrediction

from detection.data.generate import get_buffer
from detection.models.validate import compute_metrics
from detection.run import run, set_args

SRC_LANG = 'ru'
TRG_LANG = 'en'


def reverse_transform(s: str) -> str:
    return ''.join(reversed(s))


class TestFunctionality(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pass

    def setUp(self) -> None:
        pass

    def test_buffer(self):
        dataset = [
            {
                SRC_LANG: 'добрый вечер',
                TRG_LANG: 'good evening',
            },
            {
                SRC_LANG: 'прошу прощения',
                TRG_LANG: 'i am sorry',
            }
        ]
        buffer = get_buffer(dataset, reverse_transform)

        assert_that(len(buffer), equal_to(4))
        assert_that(buffer[0], equal_to('речев йырбод'))

    def test_compute_metrics(self):
        eval_pred = EvalPrediction(
            predictions=np.array([[0], [1]]),
            label_ids=np.array([0, 1]),
        )
        results = compute_metrics(eval_pred)
        metrics_names = list(results.keys())
        metrics_values = list(results.values())

        assert_that(metrics_names, equal_to(['accuracy', 'f1', 'precision', 'recall']))
        for value in metrics_values:
            assert_that(type(value), equal_to(float))


class TestBaseline(TestCase):
    def test_run(self):
        arg_parser = argparse.ArgumentParser(
            'Text Detection',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        set_args(arg_parser)
        args, _ = arg_parser.parse_known_args()

        args.run_name = 'test_run'
        args.epochs = 1
        args.size = 128
        args.cuda = torch.cuda.is_available()
        args.device = torch.device(f'cuda:{torch.cuda.current_device()}' if torch.
                                   cuda.is_available() else 'cpu')
        trainer = run(args)
        test_model_name = 'test_model.pth'
        trainer.model.save_pretrained(test_model_name)

        if os.path.exists(test_model_name):
            shutil.rmtree(test_model_name)
