import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

def capture_screenshots():
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        # 1920x1080 viewport for clean 16:9 1080p presentation slides
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
        )
        page = context.new_page()

        def wait_for_streamlit():
            page.wait_for_timeout(1500)
            # Wait for any Streamlit running spinners to disappear
            try:
                page.wait_for_selector('[data-testid="stStatusWidget"]', state="hidden", timeout=5000)
            except Exception:
                pass
            page.wait_for_timeout(1000)

        def click_tab(tab_name):
            tab = page.locator(f'button[role="tab"]:has-text("{tab_name}")').first
            tab.click()
            wait_for_streamlit()

        def reset_scenario():
            reset_btn = page.locator('button:has-text("Reset Scenario Data")').first
            if reset_btn.is_visible():
                reset_btn.click()
                wait_for_streamlit()

        def generate_plan():
            plan_btn = page.locator('button:has-text("Generate Response Plan")').first
            plan_btn.click()
            wait_for_streamlit()

        print("Opening app...")
        page.goto("http://localhost:8501", wait_until="networkidle")
        wait_for_streamlit()

        # -------------------------------------------------------------
        # 1. 01_situation.png
        # -------------------------------------------------------------
        print("Capturing 01_situation.png...")
        reset_scenario()
        generate_plan()
        click_tab("Situation")

        # Check toggle "Show evacuation assignments on map"
        # It's default ON, but let's verify
        toggle_loc = page.locator('label:has-text("Show evacuation assignments on map") input[type="checkbox"]').first
        if toggle_loc.is_visible():
            if not toggle_loc.is_checked():
                page.locator('label:has-text("Show evacuation assignments on map")').click()
                wait_for_streamlit()

        # Let Plotly map render completely
        page.wait_for_timeout(2000)
        # Scroll to top so header, KPI strip, and situation map are all visible
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)
        page.screenshot(path=str(screenshots_dir / "01_situation.png"))
        print("  -> Saved 01_situation.png")

        # -------------------------------------------------------------
        # 2. 02_agent_run.png
        # -------------------------------------------------------------
        print("Capturing 02_agent_run.png...")
        click_tab("Agent Run")
        # Scroll so top of tab is visible (KPIs + Convergence banner + red Critic rejection + green rework callout)
        # In app.py, the tab contents start below the tabs bar.
        # Let's scroll element into view if needed, or scroll to show banner + callouts
        banner_loc = page.locator('text="Adversarial Critic Convergence"').first
        if banner_loc.is_visible():
            banner_loc.scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        page.screenshot(path=str(screenshots_dir / "02_agent_run.png"))
        print("  -> Saved 02_agent_run.png")

        # -------------------------------------------------------------
        # 3. 03_naive_vs_verified.png
        # -------------------------------------------------------------
        print("Capturing 03_naive_vs_verified.png...")
        click_tab("Final Plan")
        # Turn ON toggle "Show plan without Critic"
        critic_toggle = page.locator('label:has-text("Show plan without Critic")').first
        if critic_toggle.is_visible():
            critic_toggle.click()
            wait_for_streamlit()

        # Scroll so the comparison header and side-by-side tables with violation cards are in view
        cmp_header = page.locator('text="Critic Side-by-Side Comparison"').first
        if cmp_header.is_visible():
            cmp_header.scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        page.screenshot(path=str(screenshots_dir / "03_naive_vs_verified.png"))
        print("  -> Saved 03_naive_vs_verified.png")

        # -------------------------------------------------------------
        # 4. 04_disruption.png
        # -------------------------------------------------------------
        print("Capturing 04_disruption.png...")
        click_tab("Disruption")
        bridge_btn = page.locator('button:has-text("Apply Bridge Failure")').first
        if bridge_btn.is_visible():
            bridge_btn.click()
            wait_for_streamlit()

        page.wait_for_timeout(2000)
        # Scroll to incident banner & diff table & before/after maps
        inc_banner = page.locator('text="Active Incident: BRIDGE WASHOUT"').first
        if inc_banner.is_visible():
            inc_banner.scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        page.screenshot(path=str(screenshots_dir / "04_disruption.png"))
        print("  -> Saved 04_disruption.png")

        # -------------------------------------------------------------
        # 5. 05_validation.png
        # -------------------------------------------------------------
        print("Capturing 05_validation.png...")
        click_tab("Validation")
        page.wait_for_timeout(2000)
        val_heading = page.locator('text="Adversarial Validation & Operational Benchmark"').first
        if val_heading.is_visible():
            val_heading.scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        page.screenshot(path=str(screenshots_dir / "05_validation.png"))
        print("  -> Saved 05_validation.png")

        # -------------------------------------------------------------
        # 6. 06_why_this.png
        # -------------------------------------------------------------
        print("Capturing 06_why_this.png...")
        click_tab("Final Plan")
        # Turn OFF toggle "Show plan without Critic" if it was on
        critic_checkbox = page.locator('label:has-text("Show plan without Critic") input[type="checkbox"]').first
        if critic_checkbox.is_visible() and critic_checkbox.is_checked():
            page.locator('label:has-text("Show plan without Critic")').click()
            wait_for_streamlit()

        # Find and expand Fernbank (V10) card
        # In app.py: with st.expander(f"{icon} {a['village_name']} ({vid}) ➔ {sh_name} via {rid} | Safety Margin: {margin:.0f}m"):
        v10_expander = page.locator('summary:has-text("Fernbank (V10)")').first
        if v10_expander.is_visible():
            v10_expander.click()
            wait_for_streamlit()
            v10_expander.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
            page.screenshot(path=str(screenshots_dir / "06_why_this.png"))
            print("  -> Saved 06_why_this.png")
        else:
            print("  Warning: Fernbank (V10) expander not found by text!")

        browser.close()
        print("All screenshots captured successfully!")

if __name__ == "__main__":
    capture_screenshots()
