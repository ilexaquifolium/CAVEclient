from re import match
from .conftest import test_info, TEST_LOCAL_SERVER, TEST_DATASTACK
import pytest
import responses
import numpy as np
from annotationframeworkclient.endpoints import (
    chunkedgraph_endpoints_v1,
    chunkedgraph_endpoints_common,
)
import datetime
import time
from urllib.parse import urlencode


def binary_body_match(body):
    def match(request_body):
        return body == request_body

    return match


class TestChunkedgraph:

    _default_endpoint_map = {
        "cg_server_address": TEST_LOCAL_SERVER,
        "table_id": test_info["segmentation_source"].split("/")[-1],
    }

    @responses.activate
    def test_get_roots(self, myclient):
        endpoint_mapping = self._default_endpoint_map
        url = chunkedgraph_endpoints_v1["get_roots"].format_map(endpoint_mapping)
        svids = np.array([97557743795364048, 75089979126506763], dtype=np.uint64)
        root_ids = np.array([864691135217871271, 864691135566275148], dtype=np.uint64)
        now = datetime.datetime.utcnow()
        query_d = {"timestamp": time.mktime(now.timetuple())}
        qurl = url + "?" + urlencode(query_d)
        responses.add(
            responses.POST,
            url=qurl,
            body=root_ids.tobytes(),
            match=[binary_body_match(svids.tobytes())],
        )

        new_root_ids = myclient.chunkedgraph.get_roots(svids, timestamp=now)
        assert np.all(new_root_ids == root_ids)
        myclient.chunkedgraph._default_timestamp = now
        new_root_ids = myclient.chunkedgraph.get_roots(svids)
        assert np.all(new_root_ids == root_ids)

        query_d = {"timestamp": time.mktime(now.timetuple()), "stop_layer": 3}
        qurl = url + "?" + urlencode(query_d)
        responses.add(
            responses.POST,
            url=qurl,
            body=root_ids.tobytes(),
            match=[binary_body_match(svids.tobytes())],
        )
        new_root_ids = myclient.chunkedgraph.get_roots(
            svids, timestamp=now, stop_layer=3
        )
        assert np.all(new_root_ids == root_ids)

        endpoint_mapping["supervoxel_id"] = svids[0]
        url = chunkedgraph_endpoints_v1["handle_root"].format_map(endpoint_mapping)
        query_d = {"timestamp": time.mktime(now.timetuple())}
        qurl = url + "?" + urlencode(query_d)
        responses.add(responses.GET, url=qurl, json={"root_id": int(root_ids[0])})
        qroot_id = myclient.chunkedgraph.get_root_id(svids[0], timestamp=now)
        assert qroot_id == root_ids[0]

    @responses.activate
    def test_get_leaves(self, myclient):
        endpoint_mapping = self._default_endpoint_map
        root_id = 864691135217871271
        endpoint_mapping["root_id"] = root_id
        url = chunkedgraph_endpoints_v1["leaves_from_root"].format_map(endpoint_mapping)

        bad_bounds = np.array([[0, 0, 0, 2], [100, 100, 100, 0]])
        with pytest.raises(ValueError):
            myclient.chunkedgraph.get_leaves(root_id, bounds=bad_bounds)

        bounds = np.array([[0, 0, 0], [100, 200, 300]]).T
        bounds_str = "0-100_0-200_0-300"
        query_d = {"bounds": bounds_str}
        urlq = url + "?" + urlencode(query_d)

        svlist = [97557743795364048, 75089979126506763]
        svids = np.array(svlist, dtype=np.int64)
        responses.add(responses.GET, json={"leaf_ids": svlist}, url=urlq)

        svids_ret = myclient.chunkedgraph.get_leaves(root_id, bounds=bounds)
        assert np.all(svids == svids_ret)

        query_d = {"bounds": bounds_str, "stop_layer": 2}
        urlq = url + "?" + urlencode(query_d)
        responses.add(responses.GET, json={"leaf_ids": svlist}, url=urlq)
        svids_ret = myclient.chunkedgraph.get_leaves(
            root_id, bounds=bounds, stop_layer=2
        )
        assert np.all(svids == svids_ret)

    @responses.activate
    def test_get_root(self, myclient):
        endpoint_mapping = self._default_endpoint_map
        root_id = 864691135217871271
        endpoint_mapping["root_id"] = root_id
        url = chunkedgraph_endpoints_v1["leaves_from_root"].format_map(endpoint_mapping)

        bad_bounds = np.array([[0, 0, 0, 2], [100, 100, 100, 0]])
        with pytest.raises(ValueError):
            myclient.chunkedgraph.get_leaves(root_id, bounds=bad_bounds)

        bounds = np.array([[0, 0, 0], [100, 200, 300]]).T
        bounds_str = "0-100_0-200_0-300"
        query_d = {"bounds": bounds_str}
        urlq = url + "?" + urlencode(query_d)

        svlist = [97557743795364048, 75089979126506763]
        svids = np.array(svlist, dtype=np.int64)
        responses.add(responses.GET, json={"leaf_ids": svlist}, url=urlq)

        svids_ret = myclient.chunkedgraph.get_leaves(root_id, bounds=bounds)
        assert np.all(svids == svids_ret)

        query_d = {"bounds": bounds_str, "stop_layer": 2}
        urlq = url + "?" + urlencode(query_d)
        responses.add(responses.GET, json={"leaf_ids": svlist}, url=urlq)
        svids_ret = myclient.chunkedgraph.get_leaves(
            root_id, bounds=bounds, stop_layer=2
        )
        assert np.all(svids == svids_ret)

    @responses.activate
    def test_merge_log(self, myclient):
        endpoint_mapping = self._default_endpoint_map
        root_id = 864691135217871271
        endpoint_mapping["root_id"] = root_id
        url = chunkedgraph_endpoints_v1["merge_log"].format_map(endpoint_mapping)

        merge_log = {
            "merge_edge_coords": [
                [[[85785, 68475, 20988]], [[85717, 67955, 20964]]],
                [[[86511, 70071, 20870]], [[86642, 70011, 20913]]],
                [[[80660, 67637, 19735]], [[80946, 67810, 19735]]],
                [[[84680, 63424, 20735]], [[84696, 63464, 20735]]],
                [[[94096, 71152, 19934]], [[94096, 71168, 19937]]],
                [[[89728, 72692, 20008]], [[89668, 72839, 19996]]],
                [[[82492, 71488, 21534]], [[82726, 71281, 21584]]],
                [[[85221, 69913, 20891]], [[85104, 70003, 20856]]],
            ],
            "merge_edges": [
                [[88393382627986340, 88322876444801990]],
                [[88534532433083295, 88604901177276829]],
                [[86985732732043081, 87056170195711450]],
                [[88040164517305351, 88040164517304487]],
                [[90645869502201091, 90645869502200218]],
                [[89450013234655197, 89450081954148949]],
                [[87479345001609186, 87549713745838644]],
                [[88182619992741827, 88182688712176449]],
            ],
        }

        responses.add(responses.GET, json=merge_log, url=url)

        qmerge_log = myclient.chunkedgraph.get_merge_log(root_id)
        assert merge_log == qmerge_log

    @responses.activate
    def test_change_log(self, myclient):
        endpoint_mapping = self._default_endpoint_map
        root_id = 864691135217871271
        endpoint_mapping["root_id"] = root_id
        url = chunkedgraph_endpoints_v1["change_log"].format_map(endpoint_mapping)

        change_log = {
            "n_mergers": 2,
            "n_splits": 2,
            "operations_ids": [178060, 178059, 178046, 178050],
            "past_ids": [
                864691135181922050,
                864691135761746230,
                864691135785389764,
                864691135583980920,
            ],
            "user_info": {
                "160": {"n_mergers": 1, "n_splits": 1},
                "161": {"n_mergers": 1},
                "164": {"n_splits": 1},
            },
        }

        responses.add(responses.GET, json=change_log, url=url)

        qchange_log = myclient.chunkedgraph.get_change_log(root_id)
        assert change_log == qchange_log

    @responses.activate
    def test_children(self, myclient):
        endpoint_mapping = self._default_endpoint_map
        root_id = 864691135217871271
        endpoint_mapping["node_id"] = root_id
        url = chunkedgraph_endpoints_v1["handle_children"].format_map(endpoint_mapping)

        children_list = [792633534440329101, 828662331442575736, 792633534440186368]
        children_ids = np.array([children_list])

        responses.add(responses.GET, json={"children_ids": children_list}, url=url)

        qchildren_ids = myclient.chunkedgraph.get_children(root_id)
        assert np.all(children_ids == qchildren_ids)

    # waiting for backend fix
    # @responses.activate
    # def test_contact_sites(self, myclient):
    #     endpoint_mapping = self._default_endpoint_map
    #     root_id = 864691135217871271
    #     endpoint_mapping['node_id']=root_id
    #     url=chunkedgraph_endpoints_v1['handle_children'].format_map(endpoint_mapping)

    #     children_list = [792633534440329101, 828662331442575736, 792633534440186368]
    #     children_ids = np.array([children_list])

    #     responses.add(responses.GET,
    #                   json={'children_ids':children_list},
    #                   url=url)

    #     qchildren_ids = myclient.chunkedgraph.get_children(root_id)
    #     assert(np.all(children_ids==qchildren_ids))

    # waiting for backend to fix to finish
    # @responses.activate
    # def test_find_path(self, myclient):
    #     endpoint_mapping = self._default_endpoint_map
    #     root_id = 864691135217871271
    #     endpoint_mapping['node_id']=root_id
    #     url=chunkedgraph_endpoints_v1['handle_children'].format_map(endpoint_mapping)

    #     children_list = [792633534440329101, 828662331442575736, 792633534440186368]
    #     children_ids = np.array([children_list])

    #     responses.add(responses.GET,
    #                   json={'children_ids':children_list},
    #                   url=url)

    #     qchildren_ids = myclient.chunkedgraph.get_children(root_id)
    #     assert(np.all(children_ids==qchildren_ids))

    @responses.activate
    def test_get_subgraph(self, myclient):
        endpoint_mapping = self._default_endpoint_map
        root_id = 864691135776832352

        bounds = np.array([[120241, 120441], [103825, 104025], [21350, 21370]])
        bounds_str = "120241-120441_103825-104025_21350-21370"

        endpoint_mapping["root_id"] = root_id
        url = chunkedgraph_endpoints_v1["get_subgraph"].format_map(endpoint_mapping)
        query_d = {"bounds": bounds_str}
        qurl = url + "?" + urlencode(query_d)
        nodes_list = [
            [97832277702483859, 97832277702483868],
            [97832277702483868, 97832277702489688],
            [97832277702505017, 97832277702505025],
        ]
        affinity_list = [2486.50634766, 7.49544525, 18.80846024]
        area_list = [2486, 7, 18]

        nodes = np.array(nodes_list, dtype=np.int64)
        affinities = np.array(affinity_list, dtype=np.float64)
        areas = np.array(area_list, dtype=np.int32)

        responses.add(
            responses.GET,
            json={"nodes": nodes_list, "affinities": affinity_list, "areas": area_list},
            url=qurl,
        )

        qnodes, qaffinities, qareas = myclient.chunkedgraph.get_subgraph(
            root_id, bounds=bounds
        )
        assert np.all(qnodes == nodes)
        assert np.all(affinities == qaffinities)
        assert np.all(areas == qareas)

    @responses.activate
    def test_get_lvl2subgraph(self, myclient):
        endpoint_mapping = self._default_endpoint_map
        root_id = 864691135776832352
        endpoint_mapping["root_id"] = root_id
        url = chunkedgraph_endpoints_v1["lvl2_graph"].format_map(endpoint_mapping)

        lvl2_graph_list = [
            [164471753114911373, 164471821834388004],
            [164471753114911373, 164542121859089069],
            [164471753114911412, 164542121859089069],
            [164471821834388004, 164542190578565862],
        ]

        lvl2_graph = np.array(lvl2_graph_list, dtype=np.int64)

        responses.add(responses.GET, json={"edge_graph": lvl2_graph_list}, url=url)

        qlvl2_graph = myclient.chunkedgraph.level2_chunk_graph(root_id)
        assert np.all(qlvl2_graph == lvl2_graph)

    @responses.activate
    def test_get_remeshing(self, myclient):
        endpoint_mapping = self._default_endpoint_map
        root_id = 864691135776832352
        endpoint_mapping["root_id"] = root_id
        url = chunkedgraph_endpoints_v1["remesh_level2_chunks"].format_map(
            endpoint_mapping
        )

        chunkid_list = [164471753114911373, 164471821834388004]

        chunk_ids = np.array(chunkid_list, dtype=np.int64)

        responses.add(
            responses.POST,
            status=200,
            url=url,
            match=[responses.json_params_matcher({"new_lvl2_ids": chunkid_list})],
        )

        myclient.chunkedgraph.remesh_level2_chunks(chunk_ids)
        myclient.chunkedgraph.remesh_level2_chunks(chunkid_list)

    @responses.activate
    def test_is_latest_roots(self, myclient):
        endpoint_mapping = self._default_endpoint_map

        url = chunkedgraph_endpoints_v1["is_latest_roots"].format_map(endpoint_mapping)

        root_id_list = [864691135776832352, 164471821834388001]
        root_ids = np.array(root_id_list, dtype=np.int64)
        is_latest_list = [True, False]
        is_latest = np.array(is_latest_list, np.bool)

        responses.add(
            responses.POST,
            status=200,
            url=url,
            json={"is_latest": is_latest_list},
            match=[responses.json_params_matcher({"node_ids": root_id_list})],
        )

        qis_latest = myclient.chunkedgraph.is_latest_roots(root_ids)
        assert np.all(is_latest == qis_latest)
        qis_latest = myclient.chunkedgraph.is_latest_roots(root_id_list)
        assert np.all(is_latest == qis_latest)

    @responses.activate
    def test_past_ids(self, myclient):
        endpoint_mapping = self._default_endpoint_map

        url = chunkedgraph_endpoints_v1["past_id_mapping"].format_map(endpoint_mapping)

        root_id_list = [864691136577570580, 864691135415612346]
        root_ids = np.array(root_id_list, np.int64)
        id_map = {
            "future_id_map": {},
            "past_id_map": {
                864691135415612346: [864691134989972295, 864691135574118596],
                864691136577570580: [864691136721486702, 864691133958789149],
            },
        }
        id_map_str = {
            "future_id_map": {},
            "past_id_map": {
                "864691135415612346": [864691134989972295, 864691135574118596],
                "864691136577570580": [864691136721486702, 864691133958789149],
            },
        }
        now = datetime.datetime.utcnow()
        past_time = now - datetime.timedelta(days=7)
        query_d = {
            "timestamp_past": time.mktime(past_time.timetuple()),
            "timestamp_future": time.mktime(now.timetuple()),
        }
        qurl = url + "?" + urlencode(query_d)
        responses.add(
            responses.GET,
            status=200,
            url=qurl,
            json=id_map_str,
            match=[responses.json_params_matcher({"root_ids": root_id_list})],
        )

        qid_map = myclient.chunkedgraph.get_past_ids(
            root_ids, timestamp_past=past_time, timestamp_future=now
        )
        assert qid_map == id_map
        qid_map = myclient.chunkedgraph.get_past_ids(
            root_id_list, timestamp_past=past_time, timestamp_future=now
        )
        assert qid_map == id_map

    def test_cloudvolume_path(self, myclient):
        cvpath = f"graphene://{TEST_LOCAL_SERVER}/segmentation/api/v1/test_v1"
        assert myclient.chunkedgraph.cloudvolume_path == cvpath

    @responses.activate
    def test_lineage_graph(self, myclient):
        endpoint_mapping = self._default_endpoint_map
        root_id = 864691136089107255
        endpoint_mapping["root_id"] = root_id
        url = chunkedgraph_endpoints_v1["handle_lineage_graph"].format_map(
            endpoint_mapping
        )
        now = datetime.datetime.utcnow()
        past_time = now - datetime.timedelta(days=7)
        query_d = {
            "timestamp_past": time.mktime(past_time.timetuple()),
            "timestamp_future": time.mktime(now.timetuple()),
        }
        qurl = url + "?" + urlencode(query_d)

        lineage_graph = {
            "directed": True,
            "graph": {},
            "links": [
                {"source": 864691136089107255, "target": 864691135490360423},
                {"source": 864691135348456151, "target": 864691136089107255},
            ],
            "multigraph": False,
            "nodes": [
                {
                    "id": 864691136089107255,
                    "operation_id": 225368,
                    "timestamp": 1616699178.177,
                },
                {
                    "id": 864691135348456151,
                    "operation_id": 217696,
                    "timestamp": 1608622183.079,
                },
                {
                    "id": 864691135490360423,
                    "operation_id": 225368,
                    "timestamp": 1618255909.638,
                },
            ],
        }
        responses.add(responses.GET, status=200, url=qurl, json=lineage_graph)

        qlineage_graph = myclient.chunkedgraph.get_lineage_graph(
            root_id, timestamp_past=past_time, timestamp_future=now
        )
        assert lineage_graph == qlineage_graph

    @responses.activate
    def test_operatin_details(self, myclient):
        endpoint_mapping = self._default_endpoint_map
        url = chunkedgraph_endpoints_v1["operation_details"].format_map(
            endpoint_mapping
        )
        operation_id_list = [225368, 217696, 225368]
        operation_ids = np.array(operation_id_list, np.int32)
        qurl = url + "?" + urlencode({"operation_ids": operation_id_list})

        operation_details = {
            "217696": {
                "bb_offset": [240, 240, 24],
                "operation_exception": "",
                "operation_status": 0,
                "operation_ts": "2021-03-25 19:06:18.177000+00:00",
                "removed_edges": [
                    [99450140208950705, 99450140208951689],
                    [99450140208950705, 99450140208952912],
                    [99450140208950716, 99450140208951689],
                    [99450140208950716, 99450140208952912],
                ],
                "roots": [864691135100007968, 864691136089107255],
                "sink_coords": [[126012, 101764, 20218], [126179, 101638, 20215]],
                "sink_ids": [99450208928441939, 99450140208946136],
                "source_coords": [[125981, 101650, 20232], [126209, 101690, 20210]],
                "source_ids": [99450140208968497, 99450140208944278],
                "timestamp": "2021-03-25 19:06:27.532000+00:00",
                "user": "121",
            },
            "225368": {
                "added_edges": [[99093279832296446, 99093279832302829]],
                "operation_exception": "",
                "operation_status": 0,
                "operation_ts": "2021-04-12 19:31:49.638000+00:00",
                "roots": [864691135490360423],
                "sink_coords": [[124760, 82888, 19383]],
                "source_coords": [[124700, 82887, 19377]],
                "timestamp": "2021-04-12 19:31:58.329000+00:00",
                "user": "121",
            },
        }

        responses.add(responses.GET, status=200, url=qurl, json=operation_details)
        # test that it works as np.array or list
        qoperation_details = myclient.chunkedgraph.get_operation_details(operation_ids)
        assert operation_details == qoperation_details

        qoperation_details = myclient.chunkedgraph.get_operation_details(
            operation_id_list
        )
        assert operation_details == qoperation_details

    @responses.activate
    def test_get_info(self, myclient):
        endpoint_mapping = self._default_endpoint_map
        url = chunkedgraph_endpoints_common["info"].format_map(endpoint_mapping)

        test_info = {
            "app": {"supported_api_versions": [0, 1]},
            "chunks_start_at_voxel_offset": True,
            "data_dir": "gs://cave_test/ws",
            "data_type": "uint64",
            "graph": {
                "bounding_box": [2048, 2048, 512],
                "chunk_size": [256, 256, 512],
                "cv_mip": 0,
                "n_bits_for_layer_id": 8,
                "n_layers": 12,
                "spatial_bit_masks": {
                    "1": 10,
                    "10": 2,
                    "11": 1,
                    "12": 1,
                    "2": 10,
                    "3": 9,
                    "4": 8,
                    "5": 7,
                    "6": 6,
                    "7": 5,
                    "8": 4,
                    "9": 3,
                },
            },
            "mesh": "cave_test_meshes",
            "mesh_metadata": {
                "uniform_draco_grid_size": 21,
                "unsharded_mesh_dir": "dynamic",
            },
            "num_channels": 1,
            "scales": [
                {
                    "chunk_sizes": [[256, 256, 32]],
                    "compressed_segmentation_block_size": [8, 8, 8],
                    "encoding": "compressed_segmentation",
                    "key": "8_8_40",
                    "locked": True,
                    "resolution": [8, 8, 40],
                    "size": [192424, 131051, 13008],
                    "voxel_offset": [26385, 30308, 14850],
                },
                {
                    "chunk_sizes": [[256, 256, 32]],
                    "compressed_segmentation_block_size": [8, 8, 8],
                    "encoding": "compressed_segmentation",
                    "key": "16_16_40",
                    "locked": True,
                    "resolution": [16, 16, 40],
                    "size": [96212, 65526, 13008],
                    "voxel_offset": [13192, 15154, 14850],
                },
                {
                    "chunk_sizes": [[256, 256, 32]],
                    "compressed_segmentation_block_size": [8, 8, 8],
                    "encoding": "compressed_segmentation",
                    "key": "32_32_40",
                    "locked": True,
                    "resolution": [32, 32, 40],
                    "size": [48106, 32763, 13008],
                    "voxel_offset": [6596, 7577, 14850],
                },
                {
                    "chunk_sizes": [[256, 256, 32]],
                    "compressed_segmentation_block_size": [8, 8, 8],
                    "encoding": "compressed_segmentation",
                    "key": "64_64_40",
                    "locked": True,
                    "resolution": [64, 64, 40],
                    "size": [24053, 16382, 13008],
                    "voxel_offset": [3298, 3788, 14850],
                },
                {
                    "chunk_sizes": [[256, 256, 32]],
                    "compressed_segmentation_block_size": [8, 8, 8],
                    "encoding": "compressed_segmentation",
                    "key": "128_128_80",
                    "resolution": [128, 128, 80],
                    "size": [12027, 8191, 6504],
                    "voxel_offset": [1649, 1894, 7425],
                },
                {
                    "chunk_sizes": [[256, 256, 32]],
                    "compressed_segmentation_block_size": [8, 8, 8],
                    "encoding": "compressed_segmentation",
                    "key": "256_256_160",
                    "resolution": [256, 256, 160],
                    "size": [6014, 4096, 3252],
                    "voxel_offset": [824, 947, 3712],
                },
                {
                    "chunk_sizes": [[256, 256, 32]],
                    "compressed_segmentation_block_size": [8, 8, 8],
                    "encoding": "compressed_segmentation",
                    "key": "512_512_320",
                    "resolution": [512, 512, 320],
                    "size": [3007, 2048, 1626],
                    "voxel_offset": [412, 473, 1856],
                },
                {
                    "chunk_sizes": [[256, 256, 32]],
                    "compressed_segmentation_block_size": [8, 8, 8],
                    "encoding": "compressed_segmentation",
                    "key": "1024_1024_640",
                    "resolution": [1024, 1024, 640],
                    "size": [1504, 1024, 813],
                    "voxel_offset": [206, 236, 928],
                },
                {
                    "chunk_sizes": [[256, 256, 32]],
                    "compressed_segmentation_block_size": [8, 8, 8],
                    "encoding": "compressed_segmentation",
                    "key": "2048_2048_1280",
                    "resolution": [2048, 2048, 1280],
                    "size": [752, 512, 407],
                    "voxel_offset": [103, 118, 464],
                },
                {
                    "chunk_sizes": [[256, 256, 32]],
                    "compressed_segmentation_block_size": [8, 8, 8],
                    "encoding": "compressed_segmentation",
                    "key": "4096_4096_2560",
                    "resolution": [4096, 4096, 2560],
                    "size": [376, 256, 204],
                    "voxel_offset": [51, 59, 232],
                },
            ],
            "sharded_mesh": True,
            "skeletons": "test_skeletons",
            "type": "segmentation",
            "verify_mesh": False,
        }

        responses.add(responses.GET, status=200, url=url, json=test_info)
        qinfo = myclient.chunkedgraph.segmentation_info
        assert test_info == qinfo

        # test twice for caching
        qinfo = myclient.chunkedgraph.segmentation_info
        assert test_info == qinfo

        base_resolution = myclient.chunkedgraph.base_resolution
        assert np.all(base_resolution == [8, 8, 40])