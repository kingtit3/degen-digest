from processor.classifier import classify


def test_classifier_tags():
    assert classify({"text": "This token rug happened"}) == "💀 Rug of the Day"
    assert classify({"text": "launch of new coin $ABC"}) == "🚀 Meme Launch"
    assert classify({"text": "whale bought 1m $PEPE"}) == "🐳 Whale Move"
