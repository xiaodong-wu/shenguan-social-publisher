#!/usr/bin/env python3
"""Offline behavioral checks; never contacts or publishes to external services."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import scrape_product as scrape
from content_plan import build_content_plan
from optimize_image import strip_metadata, compress, validate, create_transport_jpeg, inspect_metadata
from update_manifest import load_manifest, write_manifest, update_manifest, validate_post_url, SHEET_ID, SHEET_URL, IDENTITIES
from validate_campaign import validate_campaign, digest, validate_facebook, validate_linkedin, validate_transport
from validate_completion import expected_row, validate_completion

URL='https://www.shenguanwatch.com/sgw-au6952.html'
HTML='''<div class="product_gallery_main"><img src="/hero.webp"></div>
<div class="product_summary"><h1>Automatic Diving Watch</h1>
<p class="product_intro">Automatic watch with OEM customization for watch brands.</p>
<p class="product_model">SKU: SGW-AU6952</p>
<ul class="product_features"><li>Movement：Japanese movement or Swiss movement</li><li>Case: 316L stainless steel</li><li>Water Resistance: 5 ATM, 10 ATM, 20 ATM</li></ul></div>
<section class="product_detail_content"><div class="product_detail_block"><h2>Product Details</h2>
<p>SGW-AU6952 automatic watch offers OEM and ODM customization.</p>
<div class="product_detail_card_grid"><p>GENERIC MOON PHASE OPTION</p></div>
<table class="product_spec_table"><tr><th>Movement</th><td>Japanese movement or Swiss movement</td></tr><tr><th>Case</th><td>316L stainless steel</td></tr><tr><th>Glass</th><td>Mineral glass or sapphire glass</td></tr><tr><th>Water Resistance</th><td>5ATM, 10ATM, 20ATM</td></tr></table></div>
<div class="product_detail_block"><h2>Factory And Quality Control</h2><p>GENERIC FACTORY CAPACITY</p></div>
<div class="product_detail_block"><h2>FAQ</h2><p>GENERIC WARRANTY CLAIM</p></div></section>'''


def parse(html):
    p=scrape.ShenguanHTMLParser();p.raw_html=html;p.feed(html);p.close();return p


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self): self.temp.cleanup()
    def product(self):
        with patch.object(scrape,'fetch_html',return_value=parse(HTML)):
            return scrape.extract_product(URL)
    def campaign(self, mode='live'):
        product=self.product();plan=build_content_plan(product)
        from io import BytesIO
        b=BytesIO();Image.new('RGB',(1000,1000),'#b27672').save(b,'PNG')
        with patch.object(scrape,'fetch_bytes',return_value=(b.getvalue(),'image/png')):
            run=scrape.create_run(product,self.root,plan,mode)
        path=run/'manifest.json';m=load_manifest(path)
        fb='''⌚ An automatic watch gives sourcing teams a defined product category to evaluate.
⚙ Japanese or Swiss movement choices are listed for configuration discussions.
💎 Mineral or sapphire glass options should be confirmed for the intended order.
✅ A 316L stainless steel case is documented in the product specifications.

Compare the available configuration options against your brand requirements. The listed water resistance options require confirmation when choosing the final specification for your order. Keep the selected movement, glass and other details clear before moving forward with purchasing.

Contact Shenguan Watch to discuss your requirements and request product information.

'''+URL+'\n\n#Watch #AutomaticWatch #WatchDesign #WatchBrand #Sourcing #Wholesale #Wristwatch #WatchManufacturer'
        li='''Selecting a watch for a brand assortment starts with a clear specification. Buyers need to distinguish between available options and the final configuration agreed for an order. That distinction helps structure useful conversations with a supplier.

- The product is presented as an automatic watch.
- The specifications list a 316L stainless steel case.
- Japanese or Swiss movement choices are available for discussion.
- Mineral or sapphire glass options are listed for configuration review.

The SGW-AU6952 product information also describes OEM and ODM customization. Purchasing teams can use the published information to prepare questions about the movement, glass and other configuration details. The listed water resistance ratings are options to confirm; they do not establish the final rating of every order. A clear agreed specification gives both parties a practical reference for the next stage of product evaluation.

Contact Shenguan Watch with your brand requirements and sourcing questions. Request further product information and confirm the intended specification before making a purchasing decision.

'''+URL+'\n\n#Watch #WatchSourcing #PrivateLabel'
        Path(m['artifacts']['facebook_copy']).write_text(fb)
        Path(m['artifacts']['linkedin_copy']).write_text(li)
        im=Image.new('RGB',(1000,1000),'#c39988');enc,final,_=compress(strip_metadata(im),750*1024,(960,960))
        Path(m['artifacts']['social_image']).write_bytes(enc)
        create_transport_jpeg(final,Path(m['artifacts']['social_upload']))
        review={'product_url':URL,'source_review':'passed','copy_review':'passed','image_review':'passed',
                'claims':[{'claim':x,'quote':x} for x in ['SGW-AU6952','Japanese movement or Swiss movement','316L stainless steel','Mineral glass or sapphire glass']],
                'sha256':{k:digest(m['artifacts'][k]) for k in ['product_json','source_hero','facebook_copy','linkedin_copy','social_image','social_upload']}}
        write_manifest(Path(m['artifacts']['review']),review)
        return path,m
    def publish_fixture(self,path):
        # Synthetic local evidence only; fake links are never sent to a browser or service.
        for c in IDENTITIES:
            update_manifest(path,c,'pending',submission_started=True)
            ev=self.root/f'{c}.md';ev.write_text('OFFLINE TEST FIXTURE - no real publication')
            url='https://www.facebook.com/61582598850100/posts/offline-fixture' if c=='facebook' else 'https://www.linkedin.com/feed/update/urn:li:activity:123456/'
            update_manifest(path,c,'published',url=url,identity_id=IDENTITIES[c],evidence=ev)
        return load_manifest(path)
    def test_actual_template_extraction_and_source_boundaries(self):
        p=self.product()
        self.assertEqual(p['model'],'SGW-AU6952');self.assertEqual(p['facts']['declared']['water_resistance'],'5 ATM, 10 ATM, 20 ATM')
        self.assertNotIn('GENERIC',p['product_detail_text']);self.assertFalse(p['facts']['conflicts'])
    def test_conflicting_units_remain_conflicts(self):
        d,c,conf=scrape.extract_facts([('Water Resistance','3 ATM')],[('Water Resistance','20 ATM')],'')
        self.assertIn('water_resistance',conf);self.assertNotIn('water_resistance',d)
    def test_optional_subset_preserves_only_shared_choices(self):
        variations={}
        d,c,conf=scrape.extract_facts([('Strap','steel or leather or nylon')],[('Strap','steel or leather')],'',variations)
        self.assertEqual(d['strap'],'steel or leather');self.assertNotIn('strap',c)
        self.assertFalse(conf);self.assertEqual(len(variations['strap']['evidence']),2)
    def test_disjoint_and_negated_options_remain_conflicts(self):
        for first,second in [('steel or leather','nylon or rubber'),('steel or leather only','steel or leather or nylon')]:
            d,c,conf=scrape.extract_facts([('Strap',first)],[('Strap',second)],'')
            self.assertIn('strap',conf)
    def test_mixed_models_rejected(self):
        p=self.product();p['summary']+=' SGW-QU8606.'
        self.assertTrue(any('Mixed model' in x for x in scrape.source_quality_issues(p)))
    def test_other_facebook_page_permalink_rejected(self):
        with self.assertRaises(ValueError): validate_post_url('facebook','https://www.facebook.com/anotherpage/posts/123')
        self.assertTrue(validate_post_url('facebook','https://www.facebook.com/shenguanwatch/posts/123'))
    def test_linkedin_cannot_submit_before_facebook_verification(self):
        path,m=self.campaign()
        with self.assertRaises(ValueError): update_manifest(path,'linkedin','pending',submission_started=True)
        self.assertNotIn('publishing_started_at',load_manifest(path))
    def test_linkedin_share_permalink_and_company_guard(self):
        url='https://www.linkedin.com/feed/update/urn:li:share:123456?actorCompanyId=110553027'
        self.assertEqual(validate_post_url('linkedin',url),url)
        with self.assertRaises(ValueError): validate_post_url('linkedin',url.replace('110553027','999999'))
        with self.assertRaises(ValueError): validate_post_url('linkedin','https://www.linkedin.com/feed/update/urn:li:share:not-a-number')
    def test_skill_directory_cannot_be_output_root(self):
        with self.assertRaises(ValueError): scrape.resolve_output_root(str(Path(scrape.__file__).resolve().parents[1]/'runs'))
    def test_catalog_traverses_late_discovered_pagination_and_dedupes(self):
        def page(product,next_page):
            return parse(f'<div class="list_product_grid"><div class="hot_product_card"><a href="/{product}.html">{product}</a></div></div><a href="{next_page}">next</a><a href="/news.html">news</a>')
        pages={scrape.PRODUCTS_URL:page('one','/watch/2.html'),scrape.BASE_URL+'/watch/2.html':page('two','/watch/3.html'),scrape.BASE_URL+'/watch/3.html':page('one','/watch/index.html')}
        audit={}
        with patch.object(scrape,'fetch_html',side_effect=lambda u:pages[u]): pool=scrape.discover_candidates(audit)
        self.assertEqual(audit['page_count'],3);self.assertEqual(len(pool),2)
        self.assertFalse(any('news.html' in x['url'] for x in pool))
    def test_full_social_batch_needs_no_article(self):
        path,m=self.campaign();result=validate_campaign(m)
        self.assertEqual(result['status'],'validated');self.assertEqual(set(m['channels']),{'facebook','linkedin'})
    def test_stale_copy_blocks_submission(self):
        path,m=self.campaign();Path(m['artifacts']['facebook_copy']).write_text('Changed unreviewed text')
        with self.assertRaises(ValueError): update_manifest(path,'facebook','pending',submission_started=True)
        self.assertNotIn('publishing_started_at',load_manifest(path))
    def test_dry_run_cannot_publish(self):
        path,m=self.campaign('dry-run')
        with self.assertRaises(ValueError): update_manifest(path,'facebook','pending',submission_started=True)
    def test_wrong_identity_and_dashboard_are_rejected(self):
        path,m=self.campaign();update_manifest(path,'facebook','pending',submission_started=True)
        ev=self.root/'ev';ev.write_text('fixture')
        with self.assertRaises(ValueError): update_manifest(path,'facebook','published',url='https://www.facebook.com/61582598850100/posts/x',identity_id='wrong',evidence=ev)
        with self.assertRaises(ValueError): update_manifest(path,'facebook','published',url='https://www.facebook.com/profile.php?id=61582598850100',identity_id=IDENTITIES['facebook'],evidence=ev)
    def test_uncertain_submit_permanently_prevents_reselection(self):
        path,m=self.campaign();update_manifest(path,'facebook','pending',submission_started=True)
        update_manifest(path,'facebook','blocked',error='uncertain')
        m=load_manifest(path)
        self.assertTrue(m['channels']['facebook']['submission_started_at'])
        with self.assertRaises(ValueError): scrape.ensure_unsubmitted(m)
    def test_published_channel_cannot_be_reset(self):
        path,m=self.campaign();self.publish_fixture(path)
        with self.assertRaises(ValueError): update_manifest(path,'facebook','pending')
    def test_sheet_is_required_and_must_match_readback(self):
        path,m=self.campaign();m=self.publish_fixture(path)
        with self.assertRaises(ValueError): validate_completion(m)
        values=expected_row(m);vf=self.root/'values.json';write_manifest(vf,values)
        ev=self.root/'readback.json';write_manifest(ev,{'spreadsheet_id':SHEET_ID,'row':7,'values':values,'matching_rows':2})
        with self.assertRaises(ValueError): update_manifest(path,'google_sheet','reported',url=SHEET_URL,external_id=7,evidence=ev,values_file=vf)
        write_manifest(ev,{'spreadsheet_id':SHEET_ID,'row':7,'values':values,'matching_rows':1})
        update_manifest(path,'google_sheet','reported',url=SHEET_URL,external_id=7,evidence=ev,values_file=vf)
        Path(m['artifacts']['social_upload']).unlink()
        self.assertEqual(validate_completion(load_manifest(path))['status'],'complete')
        self.assertEqual(expected_row(load_manifest(path)),values)
    def test_candidate_budget_and_no_reuse(self):
        log_path,log=scrape.new_selection(self.root,targeted=False);log['mode']='dry-run'
        candidates=[{'url':f'https://www.shenguanwatch.com/p{i}.html'} for i in range(20)]
        with patch.object(scrape,'extract_product',side_effect=ValueError('bad source')) as extract:
            with self.assertRaises(RuntimeError): scrape.select_candidate(candidates,self.root,log_path,log)
            self.assertEqual(extract.call_count,10)
        self.assertEqual(len(log['attempts']),10)
    def test_network_failure_stops_after_one_candidate(self):
        log_path,log=scrape.new_selection(self.root,targeted=False);log['mode']='dry-run'
        with patch.object(scrape,'extract_product',side_effect=RuntimeError('network unavailable')) as extract:
            with self.assertRaises(RuntimeError): scrape.select_candidate([{'url':URL},{'url':URL+'x'}],self.root,log_path,log)
            self.assertEqual(extract.call_count,1)
        self.assertEqual(log['status'],'blocked')
    def test_small_image_fails_and_metadata_is_removed(self):
        with self.assertRaises(ValueError): compress(Image.new('RGB',(100,100)),750*1024,(960,960))
        image=Image.new('RGB',(1000,1000));image.info.update(exif=b'fixture',icc_profile=b'fixture',xmp=b'fixture')
        clean=strip_metadata(image);self.assertFalse(clean.info)
        enc,_,_=compress(clean,750*1024,(960,960));p=self.root/'image.webp';p.write_bytes(enc)
        self.assertTrue(validate(p,'social',750*1024)['metadata_removed'])

    def test_original_social_copy_format_is_required(self):
        path,m=self.campaign()
        fb=Path(m['artifacts']['facebook_copy']).read_text()
        li=Path(m['artifacts']['linkedin_copy']).read_text()
        self.assertEqual(validate_facebook(fb,URL)['feature_lines'],4)
        self.assertEqual(validate_linkedin(li,URL)['feature_bullets'],4)
        with self.assertRaisesRegex(ValueError,'emoji feature lines'):
            validate_facebook(fb.replace('⌚ ','',1),URL)
        with self.assertRaisesRegex(ValueError,'hashtags'):
            validate_facebook(fb.replace('#Watch ','',1),URL)
        with self.assertRaisesRegex(ValueError,'feature bullets'):
            validate_linkedin(li.replace('- ',''),URL)

    def test_unknown_jpeg_application_metadata_is_rejected(self):
        p=self.root/'upload.jpg'
        create_transport_jpeg(strip_metadata(Image.new('RGB',(1000,1000))),p)
        self.assertTrue(inspect_metadata(p)['metadata_removed'])
        raw=p.read_bytes();payload=b'non-image application fixture'
        p.write_bytes(raw[:2]+b'\xff\xeb'+(len(payload)+2).to_bytes(2,'big')+payload+raw[2:])
        self.assertIn('APP11',inspect_metadata(p)['embedded_metadata'])
        with self.assertRaisesRegex(ValueError,'metadata'):
            validate_transport(p)

if __name__=='__main__': unittest.main(verbosity=2)
