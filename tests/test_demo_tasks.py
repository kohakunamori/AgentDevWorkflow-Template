import unittest

from src.demo_tasks import Task, add_task, complete_task, list_tasks


class DemoTasksTests(unittest.TestCase):
    def test_add_task_returns_new_list_and_trims_input(self):
        previous = [Task("existing")]
        added = add_task(previous, "  new  ")
        self.assertEqual(added, [Task("existing"), Task("new")])
        self.assertEqual(previous, [Task("existing")])

    def test_blank_name_is_invalid(self):
        for title in ("", " ", "\t\n"):
            with self.subTest(title=title):
                with self.assertRaises(ValueError):
                    add_task([], title)

    def test_complete_task_is_immutable_and_idempotent(self):
        before = [Task("first"), Task("second")]
        after = complete_task(before, "first")
        self.assertEqual(before, [Task("first"), Task("second")])
        self.assertEqual(after, [Task("first", True), Task("second")])
        self.assertEqual(complete_task(after, "first"), after)

    def test_list_tasks_filter_and_order(self):
        original = [Task("a"), Task("b", True), Task("c")]
        self.assertEqual(list_tasks(original), original)
        self.assertEqual(list_tasks(original, include_completed=False), [Task("a"), Task("c")])


if __name__ == "__main__":
    unittest.main()
