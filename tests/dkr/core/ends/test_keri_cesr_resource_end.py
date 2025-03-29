import falcon
import pytest
from keri import kering
from keri.app import habbing
from mockito import mock, when

from dkr.core.ends.keri_cesr_resource_end import KeriCesrResourceEnd


def test_keri_cesr_resource_end_on_get_single_sig():
    req = mock(falcon.Request)
    rep = mock(falcon.Response)
    hby = mock(habbing.Habery)

    hab = mock()
    hab.kever = mock()
    hab.kever.wits = ['BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha']

    hby.db = mock()
    hby.db.ends = mock()
    hby.habs = {'test_aid': hab}
    hby.kevers = {'test_aid': mock()}

    req.path = '/test_aid/keri.cesr'

    mock_serder_raw = [
        bytearray(
            b'{"v":"KERI10JSON0001b7_","t":"icp","d":"EKYLUMmNPZeEs77Zvclf0bSN5IN-mLfLpx2ySb-HDlk4","i":"EKYLUMmNPZeEs77Zvclf0bSN5IN-mLfLpx2ySb-HDlk4","s":"0","kt":"1","k":["DHGb2qY9WwZ1sBnC9Ip0F-M8QjTM27ftI-3jTGF9mc6K"],"nt":"1","n":["EHlpcaxffvtcpoUUMTc6tpqAVtb2qnOYVk_3HRsZ34PH"],"bt":"2","b":["BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha","BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM","BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX"],"c":[],"a":[]}-VBq-AABAABpDqK4TQytiWO_S-2VvfigdPs6T2pEWPfbgqy7DzYhakD9EmW-wGGa7i5VoF7Re8pkCCLIAO35_BtZOfNV4WIA-BADAADBrKDUOPHm9IFvg_EeEmMMzAvXB4xu6MdnzTohJkeK3Ome__5IWtnWZmXRYyIYau5BPqVXM9RptPc2DCmDg2wKABDrSZ3pVsK7DNlSS_fcT3QO3adZyhcIxcWiJUc5dYsHlEu-A3AVu8nkqXLeYXqE9Z_JKTJen-GfHU3tVp16GPIEACDUzCmXCwY-E6bCbz7umsvnvBS2MS83-03CbCuZ3DZN1GQLlH-A3bUKlhabdqjYW56JtifgcljgGvN7mJk8oa8P-EAB0AAAAAAAAAAAAAAAAAAAAAAA1AAG2025-03-18T17c57c24d927822p00c00'
        )
    ]
    when(hby.db).clonePreIter(pre='test_aid').thenReturn(mock_serder_raw)

    when(hab).loadLocScheme(eid='BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha').thenReturn(
        bytearray(
            b'{"v":"KERI10JSON0000fa_","t":"rpy","d":"ELSHJwBjsy41VvikaWd5cSC5hoooONVeVsImCzjzBQWP","dt":"2022-01-20T12:57:59.823350+00:00","r":"/loc/scheme","a":{"eid":"BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha","scheme":"http","url":"http://127.0.0.1:5642/"}}-VAi-CABBBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha0BDRY23xEjEXaAJs7jPJt6uyxK8N2apNJitvn9mo0q4Gh8p7Pf2bAEp1Ufed5l0FdlLxV-Z2sMO8D7wVtA-m_QEM{"v":"KERI10JSON0000f8_","t":"rpy","d":"EBwDJvb5oW2SgwNfDK8Ib-NiljgBt4uK1bDjW3QztBPr","dt":"2022-01-20T12:57:59.823350+00:00","r":"/loc/scheme","a":{"eid":"BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha","scheme":"tcp","url":"tcp://127.0.0.1:5632/"}}-VAi-CABBBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha0BCsK_YJIDH8djf5ncLs0VPJ1In104Hiu1392AlIMVFhmIxDP6gxgzMtklcOIyhQwRe7Mvgjniynjdv95iTCPWEL'
        )
    )
    when(hab).makeEndRole(eid='BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha', role=kering.Roles.witness).thenReturn(
        bytearray(
            b'{"v":"KERI10JSON000113_","t":"rpy","d":"EC-u2taS5Z0YZT18XvV8cPnFDJVNjm6B7j_vZbeMBKHF","dt":"2025-03-21T14:33:26.196052+00:00","r":"/end/role/add","a":{"cid":"EKYLUMmNPZeEs77Zvclf0bSN5IN-mLfLpx2ySb-HDlk4","role":"witness","eid":"BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"}}-VA0-FABEKYLUMmNPZeEs77Zvclf0bSN5IN-mLfLpx2ySb-HDlk40AAAAAAAAAAAAAAAAAAAAAAAEKYLUMmNPZeEs77Zvclf0bSN5IN-mLfLpx2ySb-HDlk4-AABAAAsb68BJ6XGB77xP37tPiDjZOd6oB4nxshznxz6GMy1dTmvpi5yltfvTpBNLZQYlhpRzUI3K0GD_4DNTiUldHAL'
        )
    )

    when(hby.db.ends).getItemIter(keys=('test_aid', kering.Roles.mailbox)).thenReturn(
        [((None, 'mailbox', 'BDilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha'), None)]
    )
    when(hab).loadLocScheme(eid='BDilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha').thenReturn(
        bytearray(b'{BDilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha-loc-scheme}')
    )
    when(hab).makeEndRole(
        cid='test_aid', eid='BDilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha', role=kering.Roles.mailbox
    ).thenReturn(bytearray(b'{BDilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha-end-role}'))

    resource = KeriCesrResourceEnd(hby)
    resource.on_get(req, rep, 'test_aid')

    assert rep.status == falcon.HTTP_200
    assert rep.content_type == 'application/cesr'
    assert (
        rep.data
        == b'{"v":"KERI10JSON0001b7_","t":"icp","d":"EKYLUMmNPZeEs77Zvclf0bSN5IN-mLfLpx2ySb-HDlk4","i":"EKYLUMmNPZeEs77Zvclf0bSN5IN-mLfLpx2ySb-HDlk4","s":"0","kt":"1","k":["DHGb2qY9WwZ1sBnC9Ip0F-M8QjTM27ftI-3jTGF9mc6K"],"nt":"1","n":["EHlpcaxffvtcpoUUMTc6tpqAVtb2qnOYVk_3HRsZ34PH"],"bt":"2","b":["BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha","BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM","BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX"],"c":[],"a":[]}-VBq-AABAABpDqK4TQytiWO_S-2VvfigdPs6T2pEWPfbgqy7DzYhakD9EmW-wGGa7i5VoF7Re8pkCCLIAO35_BtZOfNV4WIA-BADAADBrKDUOPHm9IFvg_EeEmMMzAvXB4xu6MdnzTohJkeK3Ome__5IWtnWZmXRYyIYau5BPqVXM9RptPc2DCmDg2wKABDrSZ3pVsK7DNlSS_fcT3QO3adZyhcIxcWiJUc5dYsHlEu-A3AVu8nkqXLeYXqE9Z_JKTJen-GfHU3tVp16GPIEACDUzCmXCwY-E6bCbz7umsvnvBS2MS83-03CbCuZ3DZN1GQLlH-A3bUKlhabdqjYW56JtifgcljgGvN7mJk8oa8P-EAB0AAAAAAAAAAAAAAAAAAAAAAA1AAG2025-03-18T17c57c24d927822p00c00{"v":"KERI10JSON0000fa_","t":"rpy","d":"ELSHJwBjsy41VvikaWd5cSC5hoooONVeVsImCzjzBQWP","dt":"2022-01-20T12:57:59.823350+00:00","r":"/loc/scheme","a":{"eid":"BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha","scheme":"http","url":"http://127.0.0.1:5642/"}}-VAi-CABBBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha0BDRY23xEjEXaAJs7jPJt6uyxK8N2apNJitvn9mo0q4Gh8p7Pf2bAEp1Ufed5l0FdlLxV-Z2sMO8D7wVtA-m_QEM{"v":"KERI10JSON0000f8_","t":"rpy","d":"EBwDJvb5oW2SgwNfDK8Ib-NiljgBt4uK1bDjW3QztBPr","dt":"2022-01-20T12:57:59.823350+00:00","r":"/loc/scheme","a":{"eid":"BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha","scheme":"tcp","url":"tcp://127.0.0.1:5632/"}}-VAi-CABBBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha0BCsK_YJIDH8djf5ncLs0VPJ1In104Hiu1392AlIMVFhmIxDP6gxgzMtklcOIyhQwRe7Mvgjniynjdv95iTCPWEL{"v":"KERI10JSON000113_","t":"rpy","d":"EC-u2taS5Z0YZT18XvV8cPnFDJVNjm6B7j_vZbeMBKHF","dt":"2025-03-21T14:33:26.196052+00:00","r":"/end/role/add","a":{"cid":"EKYLUMmNPZeEs77Zvclf0bSN5IN-mLfLpx2ySb-HDlk4","role":"witness","eid":"BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"}}-VA0-FABEKYLUMmNPZeEs77Zvclf0bSN5IN-mLfLpx2ySb-HDlk40AAAAAAAAAAAAAAAAAAAAAAAEKYLUMmNPZeEs77Zvclf0bSN5IN-mLfLpx2ySb-HDlk4-AABAAAsb68BJ6XGB77xP37tPiDjZOd6oB4nxshznxz6GMy1dTmvpi5yltfvTpBNLZQYlhpRzUI3K0GD_4DNTiUldHAL{BDilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha-loc-scheme}'
    )


def test_keri_cesr_resource_end_on_get_bad_path():
    req = mock(falcon.Request)
    rep = mock(falcon.Response)
    hby = mock(habbing.Habery)
    hby.kevers = {'test_aid': mock()}

    req.path = '/test_aid/bad.path'

    resource = KeriCesrResourceEnd(hby)

    with pytest.raises(falcon.HTTPBadRequest) as e:
        resource.on_get(req, rep, 'test_aid')

    assert isinstance(e.value, falcon.HTTPBadRequest)


def test_keri_cesr_resource_end_on_get_bad_aid():
    req = mock(falcon.Request)
    rep = mock(falcon.Response)
    hby = mock(habbing.Habery)
    hby.kevers = {'test_aid': mock()}

    req.path = '/bad_aid/keri.cesr'

    resource = KeriCesrResourceEnd(hby)

    with pytest.raises(falcon.HTTPNotFound) as e:
        resource.on_get(req, rep, 'bad_aid')

    assert isinstance(e.value, falcon.HTTPNotFound)
