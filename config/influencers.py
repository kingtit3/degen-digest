#!/usr/bin/env python3
"""
Influencers configuration for enhanced viral prediction
"""

def get_influencers():
    """Get list of crypto influencers to monitor"""
    return [
        "CryptoCobain", "CryptoKaleo", "0xfoobar", "ansem", "sisyphus", "degendata",
        "DegenSpartan", "WassieCapital", "gcrclassic", "punk9059", "punk6529", "SatoshiLite",
        "TheCryptoDog", "Cobie", "CryptoDonAlt", "Gainzy222", "AltcoinPsycho", "degenharambe",
        "dilutionproof", "rektbuilder", "redphonecrypto", "inversebrah", "route2fi", "du5tm",
        "mayne", "lightcrypto", "imnotartsy", "LedgerStatus", "martiniGuyYT", "Pentosh1",
        "TraderSZ", "CryptoCred", "BitcoinMagazine", "hype_eth", "loopifyyy", "RaoulGMI",
        "elonmusk", "cz_binance", "VitalikButerin", "APompliano", "balajis", "aantonop",
        "CryptoWendyO", "TheMoonCarl", "Melt_Dem", "DTAPCAP", "CamilaRusso", "IvanOnTech",
        "chrisdixon", "WhalePanda", "saylor", "ErikVoorhees", "naval", "TheCryptoLark", 
        "bitboy_crypto", "intocryptoverse", "TySmithHQ", "MMCrypto", "AshCrypto", "CryptoRover", 
        "PlanB", "WClementeIII", "ChrisJaszczyns", "CryptoMichNL", "ilCapoOfCrypto", "ChrisOG", 
        "ERVA", "cdixon", "CathieDWood", "DasAbhyudoy", "sandeepnailwal", "adam3us", "justinsuntron", 
        "CharlesHoskinson", "laurashin", "CryptoGokhshtein", "MissTeenCrypto", "GirlGoneCrypto", 
        "CryptoTony", "Cred", "CryptoELlTES", "STEPHISCRYPTO", "TitanOfCrypto", "OTC_Bitcoin", 
        "CryptoRaven", "CryptoDeus", "CryptoBrekkie", "ScottMelker", "ToneVays", "rogerkver", 
        "pmarca", "paulg", "lopp", "DTAPCAP", "woonomic", "BenjaminCowen", "Trader_Jibon", 
        "cryptocevo", "loomdart", "KoroushAK", "AltcoinGordon", "Trader_XO", "CryptoWizardd", 
        "TraderMayne"
    ]

def get_influencer_categories():
    """Get influencers categorized by type"""
    return {
        "traders": [
            "CryptoCobain", "CryptoKaleo", "CryptoDonAlt", "Gainzy222", "AltcoinPsycho",
            "TraderSZ", "CryptoCred", "Trader_Jibon", "Trader_XO", "TraderMayne"
        ],
        "analysts": [
            "0xfoobar", "ansem", "sisyphus", "degendata", "DegenSpartan", "Cobie",
            "PlanB", "WClementeIII", "BenjaminCowen", "AltcoinGordon"
        ],
        "founders": [
            "VitalikButerin", "cz_binance", "saylor", "justinsuntron", "CharlesHoskinson",
            "sandeepnailwal", "adam3us"
        ],
        "media": [
            "BitcoinMagazine", "CryptoWendyO", "CamilaRusso", "IvanOnTech", "TheCryptoLark",
            "CryptoMichNL", "CryptoBrekkie"
        ],
        "influencers": [
            "elonmusk", "APompliano", "balajis", "aantonop", "chrisdixon", "cdixon",
            "CathieDWood", "laurashin", "pmarca", "paulg"
        ]
    }

def get_high_priority_influencers():
    """Get high-priority influencers for real-time monitoring"""
    return [
        "CryptoCobain", "CryptoKaleo", "Cobie", "VitalikButerin", "cz_binance",
        "elonmusk", "saylor", "PlanB", "BenjaminCowen"
    ] 