from cloup import Context


def test_context_settings_creation():
    assert Context.settings() == {}
    assert Context.settings(
        resilient_parsing=False, align_sections=True, formatter_settings={'width': 80}
    ) == dict(
        resilient_parsing=False, align_sections=True, formatter_settings={'width': 80}
    )
