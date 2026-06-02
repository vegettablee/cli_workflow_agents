import json
import os
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Horizontal, Vertical
from textual.widgets import Header, Footer, Label, Input, Switch, Button, Static
from textual.binding import Binding
from textual import on
from rich.console import Console

console = Console()

WATCHLIST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "watchlist.json"
)

MIN_TIMEOUT = 1
MAX_TIMEOUT = 120


def _load_watchlist() -> dict:
    with open(WATCHLIST_PATH, "r") as f:
        return json.load(f)


def _save_watchlist(config: dict):
    with open(WATCHLIST_PATH, "w") as f:
        json.dump(config, f, indent=2)


class SectionHeader(Static):
    DEFAULT_CSS = "SectionHeader { color: cyan; text-style: bold; margin-top: 1; }"


class ErrorMessage(Static):
    DEFAULT_CSS = "ErrorMessage { color: red; margin-top: 1; }"


class ScraperConfigApp(App):
    CSS = """
    Screen {
        padding: 1 2;
    }
    Header {
        background: #000000;
        color: white;
    }
    Footer {
        background: #000000;
        color: white;
    }
    .field-row {
        height: auto;
        margin-bottom: 1;
    }
    .field-label {
        width: 20;
        padding-top: 1;
        color: $text-muted;
    }
    .field-input {
        width: 30;
    }
    .brand-row {
        height: 3;
        margin-bottom: 0;
    }
    .brand-label {
        width: 30;
        padding-top: 1;
    }
    .action-bar {
        margin-top: 2;
        height: 5;
    }
    #error {
        color: red;
        height: auto;
        margin-top: 1;
    }
    #stats-btn {
        margin-left: 4;
    }
    #categories-bar {
        height: auto;
        padding-top: 1;
    }
    .cat-btn {
        margin-right: 1;
        min-width: 12;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
    ]

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.should_start = False
        self._cat_states: dict[str, bool] = {
            cat: True for cat in config["global"]["categories"]
        }
        self._cat_id_map: dict[str, str] = {
            f"cat_{cat.replace('-', '_').replace(' ', '_')}": cat
            for cat in config["global"]["categories"]
        }

    def compose(self) -> ComposeResult:
        g = self.config["global"]
        yield Header(show_clock=False)

        with ScrollableContainer():
            yield SectionHeader("── Global Settings ──────────────────────")

            with Horizontal(classes="field-row"):
                yield Label("Timeout (min)", classes="field-label")
                yield Input(
                    str(g["sub_agent_timeout_minutes"]),
                    id="timeout",
                    classes="field-input",
                    placeholder="1-120"
                )

            with Horizontal(classes="field-row"):
                yield Label("Price Ceiling", classes="field-label")
                yield Input(
                    str(g["price_ceiling"]) if g["price_ceiling"] else "",
                    id="price_ceiling",
                    classes="field-input",
                    placeholder="e.g. 500 (blank = none)"
                )

            with Horizontal(classes="field-row"):
                yield Label("Condition", classes="field-label")
                yield Input(
                    ", ".join(g["condition"]),
                    id="condition",
                    classes="field-input",
                    placeholder="e.g. excellent, good"
                )

            with Horizontal(classes="field-row"):
                yield Label("Categories", classes="field-label")
                with Horizontal(id="categories-bar"):
                    for cat in self._cat_states:
                        cat_id = f"cat_{cat.replace('-', '_').replace(' ', '_')}"
                        yield Button(cat, id=cat_id, classes="cat-btn", variant="primary")

            with Horizontal(classes="field-row"):
                yield Label("Clothing Sizes", classes="field-label")
                yield Input(
                    ", ".join(g["sizes"]["clothing"]),
                    id="sizes_clothing",
                    classes="field-input",
                    placeholder="e.g. M, L"
                )

            with Horizontal(classes="field-row"):
                yield Label("Denim Sizes", classes="field-label")
                yield Input(
                    ", ".join(g["sizes"]["denim"]),
                    id="sizes_denim",
                    classes="field-input",
                    placeholder="e.g. M"
                )

            with Horizontal(classes="field-row"):
                yield Label("Shoe Sizes", classes="field-label")
                yield Input(
                    ", ".join(g["sizes"]["shoes"]),
                    id="sizes_shoes",
                    classes="field-input",
                    placeholder="e.g. M"
                )

            yield SectionHeader("── Sources (at least one required) ──────")

            for source, enabled in g["sources"].items():
                with Horizontal(classes="brand-row"):
                    yield Label(source.capitalize(), classes="brand-label")
                    yield Switch(value=enabled, id=f"source_{source}")

            yield SectionHeader("── Brands (at least one required) ───────")

            for brand in self.config["brands"]:
                brand_id = brand["name"].lower().replace(" ", "_")
                with Horizontal(classes="brand-row"):
                    yield Label(brand["name"], classes="brand-label")
                    yield Switch(value=brand["enabled"], id=f"brand_{brand_id}")

            yield ErrorMessage("", id="error")

            with Horizontal(classes="action-bar"):
                yield Button("Start Scraping", id="start-btn", variant="success")
                yield Button("View Stats (coming soon)", id="stats-btn", variant="default", disabled=True)

        yield Footer()

    def _collect_config(self) -> tuple[dict | None, str]:
        g = self.config["global"]

        # Timeout safeguard
        timeout_val = self.query_one("#timeout", Input).value.strip()
        try:
            timeout = int(timeout_val)
            if timeout < MIN_TIMEOUT or timeout > MAX_TIMEOUT:
                return None, f"Timeout must be between {MIN_TIMEOUT} and {MAX_TIMEOUT} minutes."
        except ValueError:
            return None, "Timeout must be a valid integer."

        # Sources safeguard
        sources = {}
        for source in g["sources"]:
            sources[source] = self.query_one(f"#source_{source}", Switch).value
        if not any(sources.values()):
            return None, "At least one source must be enabled."

        # Brands safeguard
        updated_brands = []
        for brand in self.config["brands"]:
            brand_id = brand["name"].lower().replace(" ", "_")
            enabled = self.query_one(f"#brand_{brand_id}", Switch).value
            updated_brands.append({**brand, "enabled": enabled})
        if not any(b["enabled"] for b in updated_brands):
            return None, "At least one brand must be enabled."

        price_raw = self.query_one("#price_ceiling", Input).value.strip()
        price_ceiling = int(price_raw) if price_raw.isdigit() else None

        condition = [c.strip() for c in self.query_one("#condition", Input).value.split(",") if c.strip()]
        categories = [cat for cat, enabled in self._cat_states.items() if enabled]
        clothing = [s.strip() for s in self.query_one("#sizes_clothing", Input).value.split(",") if s.strip()]
        denim = [s.strip() for s in self.query_one("#sizes_denim", Input).value.split(",") if s.strip()]
        shoes = [s.strip() for s in self.query_one("#sizes_shoes", Input).value.split(",") if s.strip()]

        updated_config = {
            **self.config,
            "global": {
                **g,
                "sub_agent_timeout_minutes": timeout,
                "price_ceiling": price_ceiling,
                "condition": condition,
                "categories": categories,
                "sources": sources,
                "sizes": {"clothing": clothing, "denim": denim, "shoes": shoes},
            },
            "brands": updated_brands,
        }

        return updated_config, ""

    @on(Button.Pressed)
    def handle_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id in self._cat_id_map:
            cat = self._cat_id_map[btn_id]
            self._cat_states[cat] = not self._cat_states[cat]
            event.button.variant = "primary" if self._cat_states[cat] else "default"
        elif btn_id == "start-btn":
            updated_config, error = self._collect_config()
            if error:
                self.query_one("#error", ErrorMessage).update(f"⚠ {error}")
                return
            _save_watchlist(updated_config)
            self.config = updated_config
            self.should_start = True
            self.exit()


def open_scraper_display():
    config = _load_watchlist()
    app = ScraperConfigApp(config)
    app.run()

    if app.should_start:
        console.print("\n[green]Configuration saved. Starting scraper session...[/green]\n")
        # TODO: hand off to scraper workflow