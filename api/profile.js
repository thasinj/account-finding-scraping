export default async function handler(req, res) {
  try {
    const { username } = req.query;
    if (!username) {
      res.status(400).json({ message: "Missing required query param 'username'" });
      return;
    }

    const apiKey = process.env.INSTAGRAM_API_KEY;
    if (!apiKey) {
      res.status(500).json({ message: 'Server misconfiguration: INSTAGRAM_API_KEY not set' });
      return;
    }

    const baseUrl = 'https://instagram-scraper-stable-api.p.rapidapi.com';
    const url = `${baseUrl}/ig_get_fb_profile_hover.php?username_or_url=${encodeURIComponent(String(username))}`;

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




