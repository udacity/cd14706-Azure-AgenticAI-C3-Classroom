import os
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, PartitionKey
from azure.identity import DefaultAzureCredential
from rag.retriever import embed_texts, get_cosmos_client

async def delete_all_items(partition_key: str):
    """Delete all items with the specified partition key to prevent contamination between runs"""
    try:
        client, container = get_cosmos_client()
        # Query all items with the specified partition key
        query = "SELECT c.id FROM c WHERE c.pk = @pk"
        params = [{"name": "@pk", "value": partition_key}]
        items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
        
        # Delete each item
        deleted_count = 0
        for item in items:
            try:
                # Use item["id"] as partition_key since COSMOS_PARTITION_KEY=/id
                container.delete_item(item=item["id"], partition_key=item["id"])
                deleted_count += 1
            except Exception as e:
                error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
                print(f"Warning: Failed to delete item {item['id']}: {error_msg}")
        
        if deleted_count > 0:
            print(f"🧹 Cleaned up {deleted_count} items with partition key '{partition_key}'")
        return deleted_count
    except Exception as e:
        print(f"Failed to cleanup items: {e}")
        return 0

async def upsert_snippet(doc_id, text, pk="ecommerce"):
    """Upsert a document with its embedding into Cosmos DB"""
    try:
        client, container = get_cosmos_client()
        embeddings = await embed_texts([text])
        vec = embeddings[0]
        keywords = text.split(':')[0] if ':' in text else text[:100]
        container.upsert_item({
            "id": doc_id,
            "pk": pk,
            "text": text,
            "keywords": keywords,
            "embedding": vec
        })
        print(f"{doc_id} upserted with Semantic Kernel embeddings.")
    except Exception as e:
        print(f"Failed to upsert {doc_id}: {e}")

async def upsert_all_ecommerce_data():
    """Upsert all optimized ecommerce product data with keyword-rich descriptions"""
    # Optimized ecommerce products with keyword-rich descriptions for better vector search
    products = [
        ("product-001", "HEADPHONES WIRELESS BLUETOOTH NOISE CANCELING ANC AUDIO MUSIC PREMIUM: AudioTech premium wireless bluetooth over-ear headphones with active noise canceling ANC technology perfect for music lovers travelers audiophiles. Long 30-hour battery life for extended listening sessions flights commutes. Quick charge feature gives 5 hours playback in 10 minutes. Bluetooth 5.0 connectivity. Comfortable memory foam ear cushions all-day wear. Perfect for music podcasts audiobooks movies gaming. Price $199.99. In stock 45 units. Superior sound quality isolation immersive audio experience."),

        ("product-002", "FITNESS WATCH TRACKER WEARABLE SMARTWATCH HEALTH HEART RATE GPS: FitTrack advanced smart fitness watch wearable tracker for athletes runners health enthusiasts. Continuous 24/7 heart rate monitoring GPS tracking outdoor activities running cycling. Sleep tracking analyzes quality stages. 7-day battery life. 50-meter water resistance swimming safe. Compatible iOS iPhone Android smartphones. Tracks steps calories distance active minutes. Multiple sport modes running cycling swimming yoga weightlifting. Price $149.99. In stock 23 units. Smartphone notifications calls texts emails apps."),

        ("product-003", "COFFEE BEANS ORGANIC ETHIOPIAN PREMIUM SPECIALTY SINGLE ORIGIN: Artisan Roast premium single-origin organic Ethiopian coffee beans from high-altitude East Africa farms. Medium roast profile fruity floral notes bright acidity complex flavor. Fair trade certified ethical sourcing roasted fresh weekly maximum freshness. Perfect pour-over French press drip espresso brewing. Tasting notes blueberry jasmine citrus honey. Price $24.99. In stock 67 units. 12oz whole bean bag ideal coffee enthusiasts home baristas specialty coffee lovers."),

        ("product-004", "LAPTOP STAND ERGONOMIC DESK MACBOOK ADJUSTABLE ALUMINUM: ErgoDesk adjustable aluminum laptop stand compatible MacBook Pro Air Dell XPS HP Lenovo ThinkPad all brands. Creates ergonomic workspace reduces neck strain back pain improves posture work from home. Height adjustable multiple angles foldable portable travel design. Fits 13-17 inch laptops. Non-slip silicone pads protect device. Ventilated cooling airflow. Price $39.99. In stock 12 units. Perfect home office remote work students professionals desk accessories."),

        ("product-005", "YOGA MAT EXERCISE FITNESS NON-SLIP WORKOUT PILATES STRETCHING: ZenFlow professional-grade non-slip yoga mat perfect home workouts studio practice pilates stretching floor exercises. Premium cushioning joint protection comfort yoga poses asanas. Extra large 72x24 inches ample space. 6mm thickness optimal balance comfort. TPE eco-friendly material non-toxic biodegradable. Includes carrying strap alignment guides. Price $49.99. In stock 34 units. Suitable Hatha Vinyasa Ashtanga Hot Yoga Bikram. Easy clean water soap."),

        ("product-006", "KEYBOARD GAMING MECHANICAL RGB ESPORTS CHERRY MX SWITCHES PROGRAMMABLE: GameTech Pro mechanical gaming keyboard designed competitive esports PC gaming professional gamers. Cherry MX Red mechanical switches fast linear response tactile feedback precision. Full RGB backlit customizable per-key lighting effects multiple color modes. Programmable macro keys custom commands detachable wrist rest comfort. USB passthrough anti-ghosting n-key rollover technology. Price $129.99. In stock 28 units. Compatible Windows Mac Linux. Perfect FPS CS:GO Valorant Call of Duty MOBA League Legends Dota 2 MMO gaming."),

        ("product-007", "MOUSE GAMING WIRELESS PRECISION FPS DPI SENSOR PROGRAMMABLE: GameTech Pro high-precision wireless gaming mouse engineered FPS first-person shooter MOBA multiplayer games. 16000 DPI optical sensor adjustable sensitivity gaming scenarios. Rechargeable lithium battery 70 hours continuous gaming. 6 programmable buttons custom commands RGB lighting effects. Ergonomic right-hand design reduces fatigue. Price $79.99. In stock 52 units. Low latency 2.4GHz wireless lag-free performance. Perfect competitive gaming esports tournaments streaming PC laptop desktop."),

        ("product-008", "CHAIR OFFICE ERGONOMIC MESH DESK LUMBAR SUPPORT ADJUSTABLE: ErgoDesk premium ergonomic mesh office chair all-day comfort productivity proper posture long work sessions. Advanced lumbar support adjustable backrest spine curvature lower back. Fully adjustable seat height armrests 360-degree swivel caster wheels. Supports 300lbs weight capacity. 5-year warranty. Breathable mesh back airflow prevents sweating. Price $249.99. In stock 15 units. Suitable home office corporate workspace executive remote work. Reduces back pain improves sitting posture enhances productivity."),

        ("product-009", "SHOES RUNNING ATHLETIC MARATHON TRAINING LIGHTWEIGHT CUSHIONED: RunFast lightweight performance running shoes marathon training half-marathon racing daily jogging runs. Cushioned responsive EVA foam midsole absorbs impact energy return joint protection. Available sizes 6-12 men women runners. Breathable engineered mesh upper ventilation shock absorption. Reflective safety details night running visibility. Durable rubber outsole traction. Price $89.99. In stock 41 units. Ideal road running treadmill workouts track 5K 10K training. Neutral pronation comfort performance."),

        ("product-010", "EARBUDS WIRELESS BLUETOOTH NOISE CANCELLING ANC TRUE WIRELESS: AudioTech true wireless Bluetooth earbuds active noise cancellation ANC technology immersive audio sound isolation. Ultra-compact design fits comfortably securely ears workouts running commuting travel. 8-hour battery single charge plus 24 hours charging case. Touch controls music calls. IPX5 waterproof sweat water resistance. Price $119.99. In stock 38 units. Perfect music listening podcast streaming phone calls video conferencing Zoom meetings. Compatible iPhone Android tablets laptops. Multiple ear tip sizes perfect fit."),

        ("shipping-info", "SHIPPING DELIVERY INFORMATION FREE STANDARD EXPRESS COSTS FEES INTERNATIONAL: Comprehensive shipping delivery information all orders. Free standard shipping orders over $50 minimum purchase. Standard delivery 3-5 business days USPS United States Postal Service UPS courier. Express expedited shipping 1-2 business days additional $9.99 fee. International shipping available Canada Mexico. Same-day delivery select metropolitan cities New York Los Angeles Chicago $19.99 premium rush fee. Tracking number included. PO Box delivery available continental United States."),

        ("return-policy", "RETURN EXCHANGE POLICY REFUND MONEY BACK GUARANTEE 30 DAY: Customer-friendly return exchange policy refund information. Generous hassle-free 30-day return policy window all products online store purchases. Items returned original unused condition tags attached packaging intact. Free prepaid return shipping labels email convenience. Full refunds processed issued 5-7 business days receive inspect return. Exchanges available different sizes colors styles same product. No restocking fees. Easy online return portal. Customer satisfaction guaranteed defective items replaced immediately."),

        ("warranty-info", "WARRANTY PROTECTION COVERAGE ELECTRONICS EXTENDED PLAN MANUFACTURER DEFECT: Detailed warranty protection coverage information electronics appliances devices. All electronics come standard 1-year manufacturer warranty covering defects materials workmanship normal use. Extended warranty protection plans purchase checkout up to 3 additional years coverage. Contact customer support team phone email file warranty claims service. Warranty does not include accidental damage water damage drops normal wear tear. Optional accidental damage protection plans high-value electronics computers appliances comprehensive coverage. Repair replacement manufacturer discretion. Register products online activation.")
    ]

    for product_id, product_text in products:
        await upsert_snippet(product_id, product_text, pk="ecommerce")

    print(f"✅ All {len(products)} ecommerce snippets upserted with optimized keyword-rich descriptions.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(upsert_all_ecommerce_data())
