// All requests are proxied through serverless functions under /api

export interface InstagramApiProfile {
  username: string;
  full_name?: string;
  follower_count: number;
  following_count: number;
  media_count: number;
  is_verified: boolean;
  profile_pic_url?: string;
  external_url?: string;
  biography?: string;
}

export interface HashtagSearchResponse {
  hashtag_name: string;
  profiles: InstagramApiProfile[];
  media_count: number;
  status: string;
}

export interface ApiError {
  message: string;
  status?: number;
}

class InstagramApiService {
  private baseURL = '/api';

  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    console.log('🔍 Making API request to:', url);

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    console.log('📥 Response status:', response.status, response.statusText);

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
        console.error('❌ API Error Response:', errorData);
      } catch (e) {
        console.error('❌ Failed to parse error response');
        errorData = {};
      }
      
      throw new ApiError({
        message: errorData.message || `API request failed with status ${response.status}: ${response.statusText}`,
        status: response.status,
      });
    }

    const data = await response.json();
    console.log('✅ API Response data:', data);
    return data;
  }

  async searchHashtag(hashtag: string): Promise<HashtagSearchResponse> {
    // Remove # if provided
    const cleanHashtag = hashtag.replace('#', '');
    
    console.log('🔍 Searching hashtag:', cleanHashtag);
    
    try {
      // Proxy through our serverless function
      const response = await this.makeRequest<any>(`/hashtag?tag=${encodeURIComponent(cleanHashtag)}`);
      
      // Handle different response formats
      if (response && typeof response === 'object') {
        // If response has profiles directly
        if (Array.isArray((response as any).profiles)) {
          return response;
        }
        
        // If response has data.profiles
        if ((response as any).data?.profiles) {
          return {
            hashtag_name: cleanHashtag,
            profiles: (response as any).data.profiles,
            media_count: (response as any).data.media_count || 0,
            status: 'ok'
          };
        }
        
        // If response is an array of profiles
        if (Array.isArray(response)) {
          return {
            hashtag_name: cleanHashtag,
            profiles: response as InstagramApiProfile[],
            media_count: (response as any).length || 0,
            status: 'ok'
          };
        }
        
        // If response has items or results
        if ((response as any).items || (response as any).results) {
          const profiles = (response as any).items || (response as any).results;
          return {
            hashtag_name: cleanHashtag,
            profiles: Array.isArray(profiles) ? profiles : [],
            media_count: profiles.length || 0,
            status: 'ok'
          };
        }
      }
      
      console.warn('⚠️ Unexpected response format:', response);
      throw new Error('Unexpected API response format');
      
    } catch (error) {
      console.error('❌ Error searching hashtag:', error);
      throw error;
    }
  }

  async getProfileDetails(username: string): Promise<InstagramApiProfile> {
    try {
      const response = await this.makeRequest<InstagramApiProfile>(`/profile?username=${encodeURIComponent(username)}`);
      return response;
    } catch (error) {
      console.error('❌ Error getting profile details:', error);
      throw error;
    }
  }

  async getSimilarAccounts(username: string): Promise<any> {
    try {
      const response = await this.makeRequest<any>(`/similar?username=${encodeURIComponent(username)}`);
      return response;
    } catch (error) {
      console.error('❌ Error getting similar accounts:', error);
      throw error;
    }
  }

  // Method to get top posts from hashtag (if available in API)
  async getHashtagPosts(hashtag: string, count: number = 20) {
    const cleanHashtag = hashtag.replace('#', '');
    
    try {
      const response = await this.makeRequest(`/hashtag/${cleanHashtag}/posts?count=${count}`);
      return response;
    } catch (error) {
      console.error('❌ Error getting hashtag posts:', error);
      throw error;
    }
  }

  // Test method to check if API is working
  async testConnection(): Promise<any> {
    try {
      // Ping a lightweight endpoint (use hashtag with a tiny tag)
      const response = await this.makeRequest('/hashtag?tag=test');
      return response;
    } catch (error) {
      console.error('❌ Connection test failed:', error);
      throw error;
    }
  }
}

export const instagramApi = new InstagramApiService();

// Helper function to transform API profile to app profile format
export function transformApiProfile(apiProfile: InstagramApiProfile, index: number): import('../components/generated/InstagramProfilesTable').InstagramProfile {
  return {
    id: `api-${apiProfile.username}-${index}`,
    profileName: apiProfile.username,
    followers: apiProfile.follower_count || 0,
    following: apiProfile.following_count || 0,
    posts: apiProfile.media_count || 0,
    lastScraped: new Date().toISOString(),
    verified: apiProfile.is_verified || false,
    profileUrl: `https://instagram.com/${apiProfile.username}`,
  };
} 