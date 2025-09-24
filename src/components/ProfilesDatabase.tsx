import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { AlertCircle, ExternalLink, Hash, Users, Search, Filter } from 'lucide-react';

interface Profile {
  id: number;
  username: string;
  full_name: string;
  follower_count: number;
  following_count: number;
  media_count: number;
  verified: boolean;
  private: boolean;
  profile_url: string;
  last_seen_at: string;
  discovery_vectors: string[];
  primary_category: string;
  discovery_count: number;
  discovery_methods: string[];
  run_inputs: string[];
  run_count: number;
  last_discovered_at: string;
}

interface Category {
  primary_category: string;
  count: number;
}

export default function ProfilesDatabase() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [minFollowers, setMinFollowers] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(50);
  const [total, setTotal] = useState(0);

  const fetchProfiles = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (selectedCategory !== 'all') params.append('category', selectedCategory);
      if (minFollowers > 0) params.append('minFollowers', minFollowers.toString());
      params.append('limit', itemsPerPage.toString());
      params.append('offset', ((currentPage - 1) * itemsPerPage).toString());

      const response = await fetch(`/api/profiles-list?${params}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch profiles: ${response.status}`);
      }
      
      const data = await response.json();
      setProfiles(data.profiles || []);
      setCategories(data.categories || []);
      setTotal(data.total || 0);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [selectedCategory, minFollowers, currentPage, itemsPerPage]);

  useEffect(() => {
    fetchProfiles();
  }, [fetchProfiles]);

  const filteredProfiles = useMemo(() => {
    if (!searchTerm.trim()) return profiles;
    
    const term = searchTerm.toLowerCase();
    return profiles.filter(profile => 
      profile.username.toLowerCase().includes(term) ||
      profile.full_name?.toLowerCase().includes(term) ||
      profile.discovery_vectors?.some(v => v.toLowerCase().includes(term)) ||
      profile.primary_category?.toLowerCase().includes(term)
    );
  }, [profiles, searchTerm]);

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString();
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      edm: 'bg-purple-100 text-purple-800',
      luxury: 'bg-yellow-100 text-yellow-800', 
      gaming: 'bg-blue-100 text-blue-800',
      fashion: 'bg-pink-100 text-pink-800',
      travel: 'bg-green-100 text-green-800',
      fitness: 'bg-red-100 text-red-800',
      food: 'bg-orange-100 text-orange-800',
      tech: 'bg-gray-100 text-gray-800',
      default: 'bg-gray-100 text-gray-600'
    };
    return colors[category?.toLowerCase()] || colors.default;
  };

  if (loading && profiles.length === 0) {
    return (
      <div className="p-6">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p>Loading profiles database...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
            <span className="text-red-700">Error loading profiles: {error}</span>
          </div>
        </div>
      </div>
    );
  }

  const totalPages = Math.ceil(total / itemsPerPage);

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-semibold">Profiles Database</h2>
          <p className="text-gray-600">
            {total.toLocaleString()} total profiles discovered across {categories.length} categories
          </p>
        </div>
        <button 
          onClick={fetchProfiles}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white border rounded-lg p-4 space-y-4">
        <h3 className="font-medium flex items-center">
          <Filter className="w-4 h-4 mr-2" />
          Filters
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search usernames, vectors..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-lg"
            />
          </div>

          {/* Category */}
          <select
            value={selectedCategory}
            onChange={(e) => {
              setSelectedCategory(e.target.value);
              setCurrentPage(1);
            }}
            className="px-3 py-2 border rounded-lg"
          >
            <option value="all">All Categories ({total})</option>
            {categories.map(cat => (
              <option key={cat.primary_category} value={cat.primary_category}>
                {cat.primary_category} ({cat.count})
              </option>
            ))}
          </select>

          {/* Min Followers */}
          <div>
            <input
              type="number"
              placeholder="Min followers"
              value={minFollowers || ''}
              onChange={(e) => {
                setMinFollowers(Number(e.target.value) || 0);
                setCurrentPage(1);
              }}
              className="w-full px-3 py-2 border rounded-lg"
              min="0"
              step="1000"
            />
          </div>

          {/* Page Size & Stats */}
          <div className="text-sm text-gray-600 flex items-center">
            Showing {filteredProfiles.length} of {total} profiles
          </div>
        </div>
      </div>

      {/* Profiles Table */}
      <div className="bg-white border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Profile</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Category & Vectors</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Followers</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Discovery Info</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Last Seen</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-900">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredProfiles.map((profile) => (
                <tr key={profile.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="flex items-center space-x-3">
                      <div>
                        <div className="flex items-center">
                          <span className="font-medium">@{profile.username}</span>
                          {profile.verified && (
                            <span className="ml-1 text-blue-500">✓</span>
                          )}
                          {profile.private && (
                            <span className="ml-1 text-gray-400">🔒</span>
                          )}
                        </div>
                        {profile.full_name && (
                          <div className="text-sm text-gray-600">{profile.full_name}</div>
                        )}
                      </div>
                    </div>
                  </td>
                  
                  <td className="px-4 py-3">
                    <div className="space-y-1">
                      {profile.primary_category && (
                        <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${getCategoryColor(profile.primary_category)}`}>
                          {profile.primary_category}
                        </span>
                      )}
                      {profile.discovery_vectors && profile.discovery_vectors.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {profile.discovery_vectors.slice(0, 3).map((vector, idx) => (
                            <span key={idx} className="inline-block px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">
                              {vector}
                            </span>
                          ))}
                          {profile.discovery_vectors.length > 3 && (
                            <span className="text-xs text-gray-500">
                              +{profile.discovery_vectors.length - 3} more
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </td>

                  <td className="px-4 py-3">
                    <div className="text-sm">
                      <div className="font-medium">{formatNumber(profile.follower_count)}</div>
                      <div className="text-gray-500">
                        {formatNumber(profile.following_count)} following
                      </div>
                    </div>
                  </td>

                  <td className="px-4 py-3">
                    <div className="text-sm space-y-1">
                      <div>
                        <span className="font-medium">Discovered {profile.discovery_count}x</span>
                      </div>
                      <div className="text-gray-600">
                        {profile.run_count} run{profile.run_count !== 1 ? 's' : ''}
                      </div>
                      {profile.discovery_methods && (
                        <div className="text-xs text-gray-500">
                          via {profile.discovery_methods.filter(Boolean).join(', ')}
                        </div>
                      )}
                    </div>
                  </td>

                  <td className="px-4 py-3">
                    <div className="text-sm text-gray-600">
                      {formatDate(profile.last_seen_at)}
                    </div>
                  </td>

                  <td className="px-4 py-3">
                    <a
                      href={profile.profile_url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center text-sm text-blue-600 hover:text-blue-700"
                    >
                      <ExternalLink className="w-4 h-4 mr-1" />
                      View
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Page {currentPage} of {totalPages}
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 border rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 border rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {filteredProfiles.length === 0 && !loading && (
        <div className="text-center py-12 text-gray-500">
          <Users className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p className="text-lg mb-2">No profiles found</p>
          <p>Try adjusting your filters or start a new discovery run!</p>
        </div>
      )}
    </div>
  );
}
