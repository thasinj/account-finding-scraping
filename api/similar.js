export default async function handler(req, res) {
  try {
    const { username_or_url, username } = req.query;
    const target = username_or_url || username;
    if (!target) {
      res.status(400).json({ message: "Missing query: 'username' or 'username_or_url'" });
      return;
    }

    const apiKey = process.env.INSTAGRAM_API_KEY;
    if (!apiKey) {
      res.status(500).json({ message: 'Server misconfiguration: INSTAGRAM_API_KEY not set' });
      return;
    }

    const baseUrl = 'https://instagram-scraper-stable-api.p.rapidapi.com';
    const url = `${baseUrl}/get_ig_similar_accounts.php?username_or_url=${encodeURIComponent(String(target))}`;

    const upstream = await fetch(url, {
      headers: {
        'X-RapidAPI-Key': apiKey,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
      },
      method: 'GET'
    });

    const text = await upstream.text();
    try {
      const data = JSON.parse(text);
      res.status(upstream.status).json(data);
    } catch (_) {
      res.status(upstream.status).send(text);
    }
  } catch (err) {
    res.status(500).json({ message: 'Unexpected server error', error: String(err) });
  }
}




