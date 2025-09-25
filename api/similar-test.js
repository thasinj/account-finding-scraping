// Quick test endpoint to find working similar account seeds
export default async function handler(req, res) {
  try {
    const testAccounts = [
      'luxury', 'fashion', 'beauty', 'fitness', 'travel', 'food', 
      'music', 'art', 'lifestyle', 'motivation', 'entrepreneur',
      'style', 'makeup', 'gaming', 'tech', 'sports'
    ];

    const apiKey = process.env.INSTAGRAM_API_KEY;
    const baseUrl = 'https://instagram-scraper-stable-api.p.rapidapi.com';
    
    const results = {};
    
    for (const account of testAccounts) {
      try {
        const url = `${baseUrl}/get_ig_similar_accounts.php?username_or_url=${account}`;
        const response = await fetch(url, {
          headers: {
            'X-RapidAPI-Key': apiKey,
            'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
          },
          timeout: 10000
        });
        
        if (response.ok) {
          const data = await response.json();
          results[account] = Array.isArray(data) ? data.length : 0;
        } else {
          results[account] = 'error';
        }
      } catch (err) {
        results[account] = 'timeout';
      }
      
      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    res.status(200).json(results);
  } catch (err) {
    res.status(500).json({ error: String(err) });
  }
}
