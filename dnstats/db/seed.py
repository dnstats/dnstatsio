import csv

import dnstats.db.models as models
from dnstats.db import db_session


def seed_db() -> None:
    _seed_dmarc_policy()
    _seed_spf()
    _seed_email_providers()
    _seed_ns_providers()


def _seed_spf():
    spf_policies = [
        ('+all', 'Pass', '#FF00FF'),
        ('?all', 'Neutral', '#FFBF7F'),
        ('~all', 'Soft-fail', '#72e572'),
        ('-all', 'Fail', '#8080FF'),
        ('no_policy', 'No Policy', '#FF8080')
    ]

    for spf_pol in spf_policies:
        spf_policy = models.SpfPolicy(qualifier=spf_pol[0], display_name=spf_pol[1], color=spf_pol[2])
        db_session.add(spf_policy)
        db_session.commit()


def _seed_sites(filename):
    with open(filename, 'r') as file:
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            site = models.Site(current_rank=int(row['rank']), domain=row['site'])
            db_session.add(site)
            db_session.commit()


def _seed_dmarc_policy():
    dmarc_policies = [
        ('none', 'None', '#FFBF7F'),
        ('quarantine', 'Quarantine', '#72e572'),
        ('reject', 'Reject', '#8080FF'),
        ('no_policy', 'No Policy', '#FF8080'),
        ('invalid', 'Invalid', '#FF00FF')
    ]
    for dmarc_policy in dmarc_policies:
        dmarc_policy = models.DmarcPolicy(policy_string=dmarc_policy[0], display_name=dmarc_policy[1], color=dmarc_policy[2])
        db_session.add(dmarc_policy)
        db_session.commit()


def _seed_email_providers():
    email_providers = [
        ("Google Apps", "l.google.com.", True),
        ("Office 365", "protection.outlook.", True),
        ("ProofPoint", "pphosted.com.", True),
        ("Minecast", "mimecast.com.", True),
        ("MailRoute", "mailroute.net.", True),
        ("Zoho", "zoho.com.", True),
        ("Barracuda Networks", "barracudanetworks.com.", True),
        ("FastMail", "messagingengine.com.", True),
        ("Cisco Cloud Email Security", "iphmx.com.", True),
        ("Self-Hosted", "domain.", False),
        ("Symantec Messaging Security", "messagelabs.com.", True),
        ("FireEyeCloud", "fireeyecloud.com.",True),
        ("ProofPoint Essentials", "ppe-hosted.com.", True),
        ("Amazon Web Services", "amazonaws.com.", True),
        ("DreamHost", "dreamhost.com.", True),
        ("Office 365", "eo.outlook.com.", True),
        ("OSU OpenSource Lab", "osuosl.org.", True),
        ("Gandi", "gandi.net.", True),
        ("Rackspace", "emailsrvr.com.", True),
        ("TrendMicro Hosted Email Security", "in.hes.trendmicro.com.", True),
        ("Self-Hosted", "amazon-smtp.amazon.com.", True),
        ("TrendMicro Hosted Email Security", "in.hes.trendmicro.eu.", True),
        ("Self-Hosted", "wikimedia.org.", True),
        ("GoDaddy", "secureserver.net.", True),
        ("NoMail", '{"0."}', True),
        ("QQ", "qq.com.", True),
        ("No mail", "nxdomain.", False),
        ('Unknown', 'Unknown.', False),
        ("Namecheap", ".web-hosting.com.", True),
        ("Google Apps", ".googlemail.com.", True)

    ]

    for email_provider in email_providers:
        email_provider_s = db_session.query(models.EmailProvider).filter_by(search_regex=email_provider[1]).scalar()

        if not email_provider_s:
            email_provider = models.EmailProvider(display_name=email_provider[0], search_regex=email_provider[1],
                                                 is_regex=email_provider[2])
            db_session.add(email_provider)
            db_session.commit()


def _seed_ns_providers():
    ns_providers = [
        ('DNSimple', 'dnsimple.com.', True),
        ('Hurricane Electric', 'he.net.', True),
        ('OVH', 'ovh.net.', True),
        ('CloudFlare', 'ns.cloudflare.com.', True),
        ('Amazon Web Services', '.awsdns-', True),
        ('DigitalOcean', 'digitalocean.com.', True),
        ('Inmotion Hosting', 'inmotionhosting.com.', True),
        ('GoDaddy', 'domaincontrol.com.', True),
        ('Hostgator', 'hostgator.com.', True),
        ('Wordpress', 'wordpress.com.', True),
        ('Linode', 'linode.com.', True),
        ('NameCheap', 'registrar-servers.com.', True),
        ('FastMail', 'messagingengine.com.', True),
        ('DNS Made Easy', 'dnsmadeeasy.com.', True),
        ('Gandi', 'gandi.net.', True),
        ('UltraDNS', 'ultradns.com.', True),
        ('Azure', '.azure-dns.com.', True),
        ('Alfa Hosting', '.alfahosting.info.', True),
        ('Google DNS', '.googledomains.com.', True),
        ('Mark Monitor', 'markmonitor.com.', True),
        ('Comcast Business', '.comcastbusiness.net.', True),
        ('DreamHost', '.dreamhost.com.', True),
        ('Akamai', '.akam.net.', True),
        ('Liquid Web', '.sourcedns.com.', True),
        ('Media Temple', 'mediatemple.net.', True),
        ('XSERVER', '.xserver.jp.', True),
        ('Internet Invest', '.srv53.net.', True),
        ('Flex Web Hosting', '.flexwebhosting.nl.', True),
        ('HostGator', '.hostgator.com.', True),
        ('NameCheap', '.namecheaphosting.com.', True),
        ('Self-hosted', 'Self-hosted', False),
        ('Unknown', 'Unknown.', False),
        ('Self-hosted', '.google.com', True),
        ('Self-hosted', 'twtrdns.net.', True),
        ('DynDNS', 'dynect.net', True),
        ('Self-hosted', '.msft.net.', True),
        ('Self-hosted', '.taobao.com.', True),
        ('Self-hosted', '.wikimedia.org.', True),
        ('360Safe', '.360safe.com.', True),
        ('Self-hosted', '.sina.com.', True),
        ('CDNS.CN', '.cdns.cn.', True),
        ('Self-hosted', '.vkontakte.ru.', True),
        ('Alibaba DNS', 'alibabadns.com.', True),
        ('Self-hosted', '.dig.com.', True),
        ('Self-hosted', '.automattic.com.', True),
        ('SURFnet', '.surfnet.nl.', True),
        ('No-IP (Vitalwerks LLC)', '.no-ip.com.', True),
        ('NS1.', '.nsone.net.', True),
        ('EasyDNS', '.easydns.com.', True),
        ('Self-hosted', '.apple.com.', True),
        ('Self-hosted', '.bbc.co.uk.', True),
        ('AliDNS', '.alidns.com.', True),
        ('Self-hosted', '.whatsapp.net.', True),
        ('Self-hosted', '.facebook.com.', True),
        ('Move', '.move.com.', True),
        ('MasterWeb', '.masterweb.net.', True),
        ('JD.com (Jingdong)', '.jd.com.', True),
        ('JD.com (Jingdong)', '.jdcache.com.', True),
        ('Internet Systems Consortium', '.isc.org.', True),
        ('Duodecad ITS', '.dditservices.com.', True),
        ('Self-hosted', 'bkngs.com.', True),
        ('Self-hosted', '.thomsonreuters.net.', True),
        ('Self-hosted', '.bng-ns.com.', True),
        ('HiChina', '.hichina.com.', True),
        ('DNSPod', '.dnspod.net.', True),
        ('DNS.com', '.dns.com.', True),
        ('Network Solutions', '.worldnic.com.', True),
        ('Fast24', '.fastdns24.com.', True),
        ('Fast24', '.fastdns24.eu.', True),
        ('CSC', '.cscdns.net', True),
        ('Domain.com', '.domain.com.', True),
        ('Wix', 'wixdns.net.', True),
        ('Cafe24', '.cafe24.com.', True),
        ('LightEdge', '.lightedge.com.', True),
        ('BlueHost', '.bluehost.com.', True),
        ('dinahosting', '.dinahosting.com.', True),
        ('MyHostAdmin', '.myhostadmin.net.', True),
        ('eNom', 'name-services.com.', True),
        ('RU-center', '.nic.ru.', True),
        ('ClouDNS', '.cloudns.net.', True),
        ('Name', '.name.com.', True),
        ('XinNet', '.xincache.com.', True)
    ]
    for ns_provider in ns_providers:
        nsp_s = db_session.query(models.DnsProvider).filter_by(search_regex=ns_provider[1]).scalar()
        if not nsp_s:
            nsp = models.DnsProvider(display_name=ns_provider[0], search_regex=ns_provider[1], is_regex=ns_provider[2])
            db_session.add(nsp)
            db_session.commit()
