import React, { useState, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, Hash, Users, Bug } from 'lucide-react';
import FilterBar from './FilterBar';
import ProfileDataTable from './ProfileDataTable';
import PaginationControls from './PaginationControls';
import { instagramApi, transformApiProfile, type ApiError } from '../../lib/instagram-api';

export interface InstagramProfile {
  id: string;
  profileName: string;
  followers: number;
  following: number;
  posts: number;
  lastScraped: string;
  verified: boolean;
  profileUrl: string;
}

export type SortField = 'profileName' | 'followers' | 'following' | 'posts' | 'lastScraped';
export type SortDirection = 'asc' | 'desc';

const InstagramProfilesTable: React.FC = () => {
  const [profiles, setProfiles] = useState<InstagramProfile[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [hashtag, setHashtag] = useState('');
  const [minFollowers, setMinFollowers] = useState<number | undefined>();
  const [maxFollowers, setMaxFollowers] = useState<number | undefined>();
  const [sortField, setSortField] = useState<SortField>('followers');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSearchedHashtag, setLastSearchedHashtag] = useState<string>('');
  const [showDebug, setShowDebug] = useState(false);

  // Debug mode - only show in development
  const isDevelopment = import.meta.env.DEV;

  const handleHashtagSearch = useCallback(async () => {
    if (!hashtag.trim()) return;

    setIsSearching(true);
    setError(null);
    setCurrentPage(1);

    try {
      console.log('🚀 Starting hashtag search for:', hashtag);
      const response = await instagramApi.searchHashtag(hashtag);
      
      if (response.profiles && response.profiles.length > 0) {
        const transformedProfiles = response.profiles.map((profile, index) => 
          transformApiProfile(profile, index)
        );
        setProfiles(transformedProfiles);
        setLastSearchedHashtag(hashtag);
        console.log('✅ Successfully loaded', transformedProfiles.length, 'profiles');
      } else {
        setProfiles([]);
        setError(`No profiles found for hashtag #${hashtag}. The API might not have data for this hashtag or the endpoint structure may be different.`);
      }
    } catch (err) {
      console.error('❌ Error searching hashtag:', err);
      const apiError = err as ApiError;
      
      let errorMessage = 'Failed to search hashtag. ';
      
      if (apiError.status === 404) {
        errorMessage += 'The hashtag endpoint was not found. The API might use a different endpoint structure.';
      } else if (apiError.status === 401 || apiError.status === 403) {
        errorMessage += 'Authentication failed. Please check your API key.';
      } else if (apiError.status === 429) {
        errorMessage += 'Rate limit exceeded. Please wait before making another request.';
      } else {
        errorMessage += apiError.message || 'Please check your internet connection and try again.';
      }
      
      setError(errorMessage);
      setProfiles([]);
    } finally {
      setIsSearching(false);
    }
  }, [hashtag]);

  const filteredAndSortedProfiles = useMemo(() => {
    let filtered = profiles.filter(profile => {
      const matchesSearch = profile.profileName.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesMinFollowers = minFollowers === undefined || profile.followers >= minFollowers;
      const matchesMaxFollowers = maxFollowers === undefined || profile.followers <= maxFollowers;
      return matchesSearch && matchesMinFollowers && matchesMaxFollowers;
    });

    // Sort the filtered results
    filtered.sort((a, b) => {
      let aValue = a[sortField];
      let bValue = b[sortField];
      
      if (sortField === 'lastScraped') {
        aValue = new Date(aValue as string).getTime();
        bValue = new Date(bValue as string).getTime();
      }
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
      }
      
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
      }
      
      return 0;
    });

    return filtered;
  }, [profiles, searchTerm, minFollowers, maxFollowers, sortField, sortDirection]);

  const paginatedProfiles = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filteredAndSortedProfiles.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredAndSortedProfiles, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(filteredAndSortedProfiles.length / itemsPerPage);

  const handleClearFilters = () => {
    setSearchTerm('');
    setMinFollowers(undefined);
    setMaxFollowers(undefined);
    setSortField('followers');
    setSortDirection('desc');
    setCurrentPage(1);
    setError(null);
  };

  const hasActiveFilters = searchTerm !== '' || minFollowers !== undefined || maxFollowers !== undefined;

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
    setCurrentPage(1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 p-4 md:p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-7xl mx-auto"
      >
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-2">
                Instagram Profile Explorer
              </h1>
              <p className="text-lg text-gray-600">
                Search Instagram profiles by hashtag and analyze their metrics
              </p>
            </div>
            {isDevelopment && (
              <button
                onClick={() => setShowDebug(!showDebug)}
                className="flex items-center gap-2 px-3 py-2 text-sm bg-yellow-100 hover:bg-yellow-200 border border-yellow-300 rounded-lg text-yellow-800 transition-colors"
              >
                <Bug className="w-4 h-4" />
                Debug {showDebug ? 'ON' : 'OFF'}
              </button>
            )}
          </div>
        </header>

        {/* Debug Panel - Development Only */}
        {isDevelopment && showDebug && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-xl"
          >
            <h3 className="font-semibold text-yellow-800 mb-2 flex items-center gap-2">
              <Bug className="w-4 h-4" />
              Debug Information
            </h3>
            <div className="text-sm text-yellow-700 space-y-1">
              <p><strong>API Base URL:</strong> https://instagram-scraper-stable-api.p.rapidapi.com</p>
              <p><strong>Expected Endpoint:</strong> /hashtag/{'{hashtag}'}</p>
              <p><strong>Profiles Loaded:</strong> {profiles.length}</p>
              <p><strong>Last Search:</strong> {lastSearchedHashtag || 'None'}</p>
              <p><strong>Console:</strong> Check browser console (F12) for detailed API logs</p>
            </div>
          </motion.div>
        )}

        <FilterBar
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          minFollowers={minFollowers}
          onMinFollowersChange={setMinFollowers}
          maxFollowers={maxFollowers}
          onMaxFollowersChange={setMaxFollowers}
          onClearFilters={handleClearFilters}
          hasActiveFilters={hasActiveFilters}
          hashtag={hashtag}
          onHashtagChange={setHashtag}
          onHashtagSearch={handleHashtagSearch}
          isSearching={isSearching}
        />

        {/* Error Message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3"
          >
            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-red-800 font-medium">Search Error</p>
              <p className="text-red-600 text-sm">{error}</p>
              {isDevelopment && (
                <p className="text-red-500 text-xs mt-2">
                  💡 Check the browser console (F12) for detailed API debugging information
                </p>
              )}
            </div>
          </motion.div>
        )}

        {/* Search Results Info */}
        {lastSearchedHashtag && profiles.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-xl flex items-center gap-3"
          >
            <Hash className="w-5 h-5 text-blue-500" />
            <div className="flex-1">
              <p className="text-blue-800 font-medium">
                Results for #{lastSearchedHashtag}
              </p>
              <p className="text-blue-600 text-sm">
                Found {profiles.length} profiles • Showing {Math.min(itemsPerPage, filteredAndSortedProfiles.length)} of {filteredAndSortedProfiles.length} after filters
              </p>
            </div>
            <div className="flex items-center gap-2 text-blue-600">
              <Users className="w-4 h-4" />
              <span className="text-sm font-medium">{profiles.length} profiles</span>
            </div>
          </motion.div>
        )}

        {/* Empty State */}
        {!isSearching && profiles.length === 0 && !error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12"
          >
            <Hash className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-600 mb-2">
              Ready to explore Instagram profiles
            </h3>
            <p className="text-gray-500 max-w-md mx-auto mb-4">
              Enter a hashtag above to discover Instagram profiles associated with that topic. 
              You'll see their follower counts, verification status, and more.
            </p>
            <p className="text-sm text-gray-400">
              Try popular hashtags like: travel, fashion, food, fitness, luxury
            </p>
          </motion.div>
        )}

        {/* Data Table */}
        {profiles.length > 0 && (
          <>
            <ProfileDataTable
              profiles={paginatedProfiles}
              sortField={sortField}
              sortDirection={sortDirection}
              onSort={handleSort}
            />

            <PaginationControls
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
              totalItems={filteredAndSortedProfiles.length}
              itemsPerPage={itemsPerPage}
              onItemsPerPageChange={setItemsPerPage}
            />
          </>
        )}
      </motion.div>
    </div>
  );
};

export default InstagramProfilesTable;