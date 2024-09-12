import io
from lucy import progress
import logging


class Test_Progress:
    def test_reports_progress_every_time_step_if_required(self):
        logger = logging.getLogger('test_progress_logger')
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        prog = progress.Progress(total=3, min_elapsed_sec=0)
        prog.logger = logger
        for i in range(3):
            prog.update(i)

        output_lines = log_stream.getvalue().rstrip().split('\n')
        assert len(output_lines) == 3
        assert output_lines[0].startswith('Progress: 1 / 3  (ETA: ')
        assert output_lines[1].startswith('Progress: 2 / 3  (ETA: ')
        assert output_lines[2].startswith('Progress: 3 / 3  (ETA: ')

    def test_reports_only_if_long_elapsed_time(self):
        logger = logging.getLogger('test_progress_logger')
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        prog = progress.Progress(total=3, min_elapsed_sec=10)
        prog.logger = logger
        for i in range(3):
            prog.update(i)

        assert log_stream.getvalue() == ''
