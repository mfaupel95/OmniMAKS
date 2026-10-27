import json
import sys
import unittest
from pathlib import Path
from unittest import mock

HANDEL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HANDEL))
import dauerlauf
import inventar_quellen as q


class QuellenTests(unittest.TestCase):
    def test_dynamic_registered_track_count_from_source(self):
        self.assertEqual(len(dauerlauf.SPUREN), len(set(dauerlauf.SPUREN)))
        # The expected count is deliberately derived from the runtime source.
        rows = [q.InventarEintrag("spur", name, "", status="registriert") for name in dauerlauf.SPUREN]
        self.assertEqual(len(rows), len(dauerlauf.SPUREN))

    def test_effective_freqtrade_mode_only_from_boolean(self):
        self.assertEqual(q.freqtrade_modus({}, {"dry_run": True}), "Papier")
        self.assertEqual(q.freqtrade_modus({}, {"dry_run": False}), "Live")
        self.assertEqual(q.freqtrade_modus({}, None), "Unbekannt")
        self.assertEqual(q.freqtrade_modus({}, {"dry_run": None}), "Unbekannt")

    def test_snapshots_report_containers_tasks_and_empty_processes(self):
        docker = json.dumps([{"Name":"freqtrade-a","State":"running","CreatedAt":"now"},
                             {"Name":"freqtrade-b","State":"exited"}])
        tasks = json.dumps([{"TaskName":"\\Verbesserer","State":"Ready","Enabled":False}])
        with mock.patch.dict(sys.modules, {"freqtrade_bridge": mock.Mock(bots=lambda: [])}):
            rows=q.lade_betrieb(Path("repo"), docker_snapshot=docker, task_snapshot=tasks,
                                prozess_snapshot="[]")
        self.assertEqual([r.status for r in rows if r.typ == "container"], ["running", "exited"])
        self.assertEqual([r.status for r in rows if r.typ == "routine"], ["deaktiviert"])
        self.assertFalse([r for r in rows if r.typ == "prozess"])

    def test_registered_bot_with_missing_container_is_visible(self):
        bridge=mock.Mock()
        bridge.bots.return_value=[{"name":"bot-a","container":"freqtrade-bot-a","port":1}]
        bridge.lage_fuer.return_value={"erreichbar":False}
        with mock.patch.dict(sys.modules, {"freqtrade_bridge":bridge}):
            rows=q.lade_betrieb(Path("repo"), docker_snapshot="[]", task_snapshot="[]", prozess_snapshot="[]")
        missing=[r for r in rows if r.typ == "container" and r.status == "fehlt"]
        self.assertEqual([r.name for r in missing], ["freqtrade-bot-a"])

    def test_missing_runtime_snapshots_are_unknown(self):
        with mock.patch.dict(sys.modules, {"freqtrade_bridge": mock.Mock(bots=lambda: [])}):
            rows=q.lade_betrieb(Path("repo"), docker_snapshot="", task_snapshot="", prozess_snapshot="")
        errors=[r for r in rows if r.typ == "runtime-fehler"]
        self.assertEqual(len(errors), 3)
        self.assertTrue(all(r.status == "unbekannt" and r.modus != "Papier" for r in errors))

    def test_snapshot_collection_uses_only_sanitized_read_only_arguments(self):
        with mock.patch.object(q.subprocess, "run", side_effect=[
                mock.Mock(stdout="bot\trunning\ttoday\n"),
                mock.Mock(stdout='"TaskName","Next Run Time","Status"\n"\\x","N/A","Disabled"\n'),
                mock.Mock(stdout='"python.exe","12","Console","1","1,000 K"\n')]) as run:
            docker, tasks, processes = q.sammle_runtime_snapshots()
        self.assertEqual(json.loads(docker)[0]["name"], "bot")
        self.assertFalse(json.loads(tasks)[0]["enabled"])
        self.assertEqual(json.loads(processes)[0]["name"], "python.exe")
        self.assertTrue(all("CommandLine" not in str(call.args) for call in run.call_args_list))

    def test_bot_rows_use_bridge_snapshot_without_exposing_config(self):
        bridge=mock.Mock()
        bridge.bots.return_value=[{"name":"one","port":1},{"name":"two","port":2},{"name":"three","port":3}]
        bridge.lage_fuer.side_effect=[{"erreichbar":True,"dry_run":True},
                                      {"erreichbar":True,"dry_run":True},
                                      {"erreichbar":True,"dry_run":True}]
        with mock.patch.dict(sys.modules, {"freqtrade_bridge":bridge}):
            rows=q.lade_betrieb(Path("repo"), docker_snapshot="[]", task_snapshot="[]", prozess_snapshot="[]")
        bots=[r for r in rows if r.typ == "freqtrade"]
        self.assertEqual([r.modus for r in bots], ["Papier"] * 3)
        self.assertTrue(all("dry_run" not in str(r) for r in bots))


if __name__ == "__main__":
    unittest.main()
