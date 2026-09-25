"""
Unit and Integration Tests for TinPyUI React-Competitor Features
Validates:
1. Core Reactive Hooks: use_state, use_effect, use_memo, use_ref, create_context, provide_context, use_context
2. Modern UI Primitives: Dialog, Modal, Tabs, TabList, TabTrigger, TabContent, Accordion, AccordionItem, Select, Dropdown, Tooltip, Popover, ToastContainer, toast
3. Reactive Form Validation Suite: Form, FormField, required, min_length, max_length, email, numeric, pattern, custom
4. SPA Client Router: Route dynamic parameters (:id), URL normalization, Router navigation, and rendering
"""

import unittest
import tinpyui as tin


class TestHooksSystem(unittest.TestCase):
    """Tests for React-like hooks running on O(1) fine-grained reactive signals."""

    def test_use_state_basic_and_functional(self):
        count, set_count = tin.use_state(0)
        self.assertEqual(count.value, 0)

        # Direct value setter
        set_count(10)
        self.assertEqual(count.value, 10)

        # Functional updater: set_count(lambda prev: prev + 5)
        set_count(lambda prev: prev + 5)
        self.assertEqual(count.value, 15)

    def test_use_signal(self):
        sig = tin.use_signal("initial")
        self.assertEqual(sig.value, "initial")
        sig.value = "mutated"
        self.assertEqual(sig.value, "mutated")

    def test_use_effect_lifecycle_and_cleanup(self):
        count, set_count = tin.use_state(1)
        runs = []
        cleanups = []

        def effect_fn():
            current_val = count.value
            runs.append(current_val)
            def cleanup():
                cleanups.append(current_val)
            return cleanup

        dispose = tin.use_effect(effect_fn, [count])
        # Effect executes immediately on mount
        self.assertEqual(runs, [1])
        self.assertEqual(cleanups, [])

        # Mutate dependency signal -> triggers cleanup then next effect run
        set_count(2)
        self.assertEqual(runs, [1, 2])
        self.assertEqual(cleanups, [1])

        set_count(3)
        self.assertEqual(runs, [1, 2, 3])
        self.assertEqual(cleanups, [1, 2])

        # Dispose runs final cleanup
        dispose()
        self.assertEqual(cleanups, [1, 2, 3])

    def test_use_memo(self):
        count, set_count = tin.use_state(5)
        multiplier, set_mult = tin.use_state(2)

        doubled = tin.use_memo(lambda: count.value * multiplier.value, [count, multiplier])
        self.assertEqual(doubled.value, 10)

        set_count(8)
        self.assertEqual(doubled.value, 16)

        set_mult(3)
        self.assertEqual(doubled.value, 24)

    def test_use_ref(self):
        my_ref = tin.use_ref("initial_ref")
        self.assertEqual(my_ref.current, "initial_ref")
        my_ref.current = 42
        self.assertEqual(my_ref.current, 42)

    def test_context_api(self):
        tin.create_context("theme", default="light")
        self.assertEqual(tin.use_context("theme"), "light")

        tin.provide_context("theme", "cyber-dark")
        self.assertEqual(tin.use_context("theme"), "cyber-dark")

        # Unknown context fallback
        self.assertEqual(tin.use_context("non_existent", "default_val"), "default_val")


class TestFormValidationSuite(unittest.TestCase):
    """Tests for Two-Way Reactive Form State & Live Validation."""

    def test_validation_rule_primitives(self):
        # required rule
        r = tin.required("Must not be blank")
        self.assertIsNotNone(r(None))
        self.assertIsNotNone(r(""))
        self.assertIsNotNone(r("   "))
        self.assertIsNotNone(r([]))
        self.assertIsNone(r("Valid text"))

        # min_length & max_length rules
        min_r = tin.min_length(5)
        self.assertIsNotNone(min_r("abc"))
        self.assertIsNone(min_r("abcdef"))

        max_r = tin.max_length(8)
        self.assertIsNotNone(max_r("123456789"))
        self.assertIsNone(max_r("12345"))

        # email rule
        em = tin.email()
        self.assertIsNotNone(em("invalid-email"))
        self.assertIsNotNone(em("alice@"))
        self.assertIsNone(em("alice@example.com"))

        # numeric rule
        num = tin.numeric()
        self.assertIsNotNone(num("abc"))
        self.assertIsNone(num("123"))
        self.assertIsNone(num("45.67"))

        # pattern rule
        pat = tin.pattern(r"^TIN-[0-9]{3}$")
        self.assertIsNotNone(pat("TIN-ABC"))
        self.assertIsNone(pat("TIN-123"))

        # custom rule
        cust = tin.custom(lambda v: v % 2 == 0, msg="Must be even")
        self.assertIsNotNone(cust(3))
        self.assertIsNone(cust(4))

    def test_form_field_reactive_validation(self):
        username_sig = tin.Signal("")
        field = tin.FormField(
            label="Username",
            bind=username_sig,
            rules=[tin.required(), tin.min_length(3)]
        )

        # Initially empty -> validation error
        self.assertIsNotNone(field.validate())
        self.assertEqual(field.is_valid_signal.value, True)  # initially untouched until change or explicit check

        # Mutate signal directly -> triggers live reactive validation
        username_sig.value = "al"
        self.assertEqual(field.is_valid_signal.value, False)
        self.assertTrue(len(field.error_signal.value) > 0)
        self.assertTrue(field.is_dirty.value)

        # Mutate to valid string
        username_sig.value = "alice_dev"
        self.assertEqual(field.is_valid_signal.value, True)
        self.assertEqual(field.error_signal.value, "")

    def test_form_container_lifecycle(self):
        submitted_data = {}
        submission_valid = False

        def handle_submit(data, valid):
            nonlocal submitted_data, submission_valid
            submitted_data = data
            submission_valid = valid

        email_sig = tin.Signal("test@test.com")
        age_sig = tin.Signal("25")

        with tin.Form(on_submit=handle_submit) as form:
            tin.FormField(label="Email", name="email", bind=email_sig, rules=[tin.required(), tin.email()])
            tin.FormField(label="Age", name="age", bind=age_sig, rules=[tin.numeric()])

        # Check discovered fields
        self.assertEqual(len(form._fields), 2)
        values = form.get_values()
        self.assertEqual(values["email"], "test@test.com")
        self.assertEqual(values["age"], "25")

        # Submit valid form
        is_ok = form.submit()
        self.assertTrue(is_ok)
        self.assertTrue(submission_valid)
        self.assertEqual(submitted_data["email"], "test@test.com")

        # Invalidate one field
        email_sig.value = "bad-email"
        is_ok = form.submit()
        self.assertFalse(is_ok)
        self.assertFalse(submission_valid)

        # Reset form
        form.reset()
        self.assertEqual(email_sig.value, "")
        self.assertEqual(age_sig.value, "")
        self.assertTrue(form.is_form_valid.value)


class TestModernPrimitivesSuite(unittest.TestCase):
    """Tests for Radix/Shadcn-style Modern Component Primitives."""

    def test_dialog_modal_state(self):
        closed_callback_called = False

        def on_close():
            nonlocal closed_callback_called
            closed_callback_called = True

        dialog = tin.Dialog(title="Confirm Action", open=False, on_close=on_close)
        self.assertFalse(dialog.open_signal.value)

        dialog.show()
        self.assertTrue(dialog.open_signal.value)

        dialog.close()
        self.assertFalse(dialog.open_signal.value)
        self.assertTrue(closed_callback_called)

        dialog.toggle()
        self.assertTrue(dialog.open_signal.value)

    def test_tabs_suite(self):
        active_tab_log = []
        tabs = tin.Tabs(
            default_value="account",
            on_change=lambda val: active_tab_log.append(val)
        )
        self.assertEqual(tabs.active_signal.value, "account")

        with tabs:
            with tin.TabList():
                tin.TabTrigger(label="Account", value="account")
                tin.TabTrigger(label="Billing", value="billing")
            tin.TabContent(value="account")
            tin.TabContent(value="billing")

        tabs.set_active("billing")
        self.assertEqual(tabs.active_signal.value, "billing")
        self.assertEqual(active_tab_log, ["billing"])

    def test_accordion_suite(self):
        toggled_states = []
        acc_item = tin.AccordionItem(
            title="General Settings",
            open=False,
            on_toggle=lambda s: toggled_states.append(s)
        )
        self.assertFalse(acc_item.open_signal.value)

        acc_item.toggle()
        self.assertTrue(acc_item.open_signal.value)
        self.assertEqual(toggled_states, [True])

        acc_item.toggle()
        self.assertFalse(acc_item.open_signal.value)
        self.assertEqual(toggled_states, [True, False])

    def test_select_dropdown(self):
        changed_value = ""
        select = tin.Select(
            options=["Option 1", "Option 2", "Option 3"],
            on_change=lambda v: (setattr(select, '_last_changed', v))
        )
        self.assertEqual(select.selected_signal.value, "Option 1")
        self.assertEqual(len(select.props["options"]), 3)

        select._handle_change("Option 3")
        self.assertEqual(select.selected_signal.value, "Option 3")
        self.assertEqual(select._last_changed, "Option 3")

    def test_toast_system(self):
        tin.toast.clear()
        self.assertEqual(len(tin.toast.toasts.value), 0)

        # Trigger various toast notification styles
        id1 = tin.toast.success("Build compiled successfully!", title="Compiled")
        id2 = tin.toast.error("Failed to connect to gateway", title="Error")
        id3 = tin.toast.info("Update available")

        self.assertEqual(len(tin.toast.toasts.value), 3)
        self.assertEqual(tin.toast.toasts.value[0]["variant"], "success")
        self.assertEqual(tin.toast.toasts.value[1]["variant"], "error")
        self.assertEqual(tin.toast.toasts.value[2]["variant"], "info")

        # Dismiss one toast
        tin.toast.dismiss(id2)
        self.assertEqual(len(tin.toast.toasts.value), 2)
        remaining_ids = [t["id"] for t in tin.toast.toasts.value]
        self.assertNotIn(id2, remaining_ids)

        # Clear all
        tin.toast.clear()
        self.assertEqual(len(tin.toast.toasts.value), 0)


class TestClientRouterSuite(unittest.TestCase):
    """Tests for Client-Side SPA Router with Dynamic Parameters."""

    def test_route_pattern_matching(self):
        # Static path
        r_home = tin.Route(path="/")
        self.assertEqual(r_home.match("/"), {})
        self.assertIsNone(r_home.match("/about"))

        # Static path with trailing slash normalization
        r_about = tin.Route(path="/about")
        self.assertEqual(r_about.match("/about"), {})
        self.assertEqual(r_about.match("/about/"), {})
        self.assertIsNone(r_about.match("/contact"))

        # Single dynamic parameter: /users/:id
        r_user = tin.Route(path="/users/:id")
        self.assertEqual(r_user.match("/users/42"), {"id": "42"})
        self.assertEqual(r_user.match("/users/alice"), {"id": "alice"})
        self.assertIsNone(r_user.match("/users"))
        self.assertIsNone(r_user.match("/posts/42"))

        # Multiple dynamic parameters: /orgs/:org_id/projects/:project_id
        r_proj = tin.Route(path="/orgs/:org_id/projects/:project_id")
        match_result = r_proj.match("/orgs/acme/projects/tinui")
        self.assertEqual(match_result, {"org_id": "acme", "project_id": "tinui"})

    def test_router_navigation_and_rendering(self):
        home_view = tin.Text("Home Page")
        user_view_builder = lambda: tin.Text("User Profile")

        with tin.Router(initial_path="/") as router:
            r1 = tin.Route(path="/", component=home_view)
            r2 = tin.Route(path="/users/:id", component=user_view_builder)

        # Initial path is "/"
        self.assertEqual(router.current_path.value, "/")
        self.assertEqual(router.active_route.value, r1)
        self.assertEqual(router.params.value, {})
        rendered = router.render()
        self.assertEqual(rendered, home_view)

        # Navigate to /users/777
        router.navigate("/users/777")
        self.assertEqual(router.current_path.value, "/users/777")
        self.assertEqual(router.active_route.value, r2)
        self.assertEqual(router.params.value, {"id": "777"})
        rendered = router.render()
        self.assertIsInstance(rendered, tin.Text)
        self.assertEqual(rendered.props["text"], "User Profile")


if __name__ == "__main__":
    unittest.main()
