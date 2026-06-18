import os
import pytest
import logging
import importlib
from helpers.utils import read_data

script = importlib.import_module("aci-preupgrade-validation-script")

log = logging.getLogger(__name__)
dir = os.path.dirname(os.path.abspath(__file__))

test_function = "bgp_node_ctx_pol_conflict_check"

# icurl queries
api_ectx = 'l3extRsEctx.json'
api_node = 'l3extRsNodeL3OutAtt.json'
api_pol = 'bgpRsBgpNodeCtxPol.json'


@pytest.mark.parametrize(
    "icurl_outputs, expected_result",
    [
        # No L3Outs at all
        (
            {
                api_ectx: read_data(dir, "empty.json"),
                api_node: read_data(dir, "empty.json"),
                api_pol: read_data(dir, "empty.json"),
            },
            script.PASS,
        ),
        # Two L3Outs in the same VRF, same node, same BGP Node Context Policy
        (
            {
                api_ectx: read_data(dir, "l3extRsEctx_two_outs_one_vrf.json"),
                api_node: read_data(dir, "l3extRsNodeL3OutAtt_two_outs_same_node.json"),
                api_pol: read_data(dir, "bgpRsBgpNodeCtxPol_same_pol.json"),
            },
            script.PASS,
        ),
        # Two L3Outs in the same VRF, same node, conflicting policies
        (
            {
                api_ectx: read_data(dir, "l3extRsEctx_two_outs_one_vrf.json"),
                api_node: read_data(dir, "l3extRsNodeL3OutAtt_two_outs_same_node.json"),
                api_pol: read_data(dir, "bgpRsBgpNodeCtxPol_different_pol.json"),
            },
            script.FAIL_O,
        ),
        # Same node referenced from two different VRFs with two distinct
        # policies - this is allowed (per-VRF scope)
        (
            {
                api_ectx: read_data(dir, "l3extRsEctx_two_outs_two_vrfs.json"),
                api_node: read_data(dir, "l3extRsNodeL3OutAtt_two_outs_same_node.json"),
                api_pol: read_data(dir, "bgpRsBgpNodeCtxPol_different_pol.json"),
            },
            script.PASS,
        ),
        # vPC pair (protnodes) in the same VRF with conflicting policies
        (
            {
                api_ectx: read_data(dir, "l3extRsEctx_two_outs_one_vrf.json"),
                api_node: read_data(dir, "l3extRsNodeL3OutAtt_protnodes.json"),
                api_pol: read_data(dir, "bgpRsBgpNodeCtxPol_different_pol.json"),
            },
            script.FAIL_O,
        ),
    ],
)
def test_logic(run_check, mock_icurl, expected_result):
    result = run_check()
    assert result.result == expected_result
