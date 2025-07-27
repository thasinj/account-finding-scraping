import React from 'react';
import { ChevronUp, ChevronDown, Users, Calendar, ExternalLink } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
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
interface ProfileDataTableProps {
  profiles: InstagramProfile[];
  sortField: SortField | null;
  sortDirection: SortDirection;
  onSort: (field: SortField) => void;
  loading?: boolean;
}
const ProfileDataTable: React.FC<ProfileDataTableProps> = ({
  profiles,
  sortField,
  sortDirection,
  onSort,
  loading = false
}) => {
  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toLocaleString();
  };
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };
  const getSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return <ChevronUp className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />;
    }
    return sortDirection === 'asc' ? <ChevronUp className="w-4 h-4 text-blue-600" /> : <ChevronDown className="w-4 h-4 text-blue-600" />;
  };
  if (loading) {
    return <div className="bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl overflow-hidden shadow-sm">
        <div className="p-8 text-center">
          <div className="animate-spin w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profiles...</p>
        </div>
      </div>;
  }
  if (profiles.length === 0) {
    return <div className="bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl overflow-hidden shadow-sm">
        <div className="p-12 text-center">
          <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No profiles found</h3>
          <p className="text-gray-600">Try adjusting your filters to see more results.</p>
        </div>
      </div>;
  }
  return <div className="bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl overflow-hidden shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full" role="table" aria-label="Instagram profiles data">
          <thead>
            <tr className="border-b border-gray-200/50 bg-gray-50/50">
              <th className="text-left p-4">
                <button onClick={() => onSort('profileName')} className="group flex items-center gap-2 font-semibold text-gray-900 hover:text-blue-600 transition-colors" aria-label={`Sort by profile name ${sortField === 'profileName' ? sortDirection === 'asc' ? 'descending' : 'ascending' : 'ascending'}`}>
                  Profile Name
                  {getSortIcon('profileName')}
                </button>
              </th>
              <th className="text-left p-4">
                <button onClick={() => onSort('followers')} className="group flex items-center gap-2 font-semibold text-gray-900 hover:text-blue-600 transition-colors" aria-label={`Sort by followers ${sortField === 'followers' ? sortDirection === 'asc' ? 'descending' : 'ascending' : 'ascending'}`}>
                  Followers
                  {getSortIcon('followers')}
                </button>
              </th>
              <th className="text-left p-4 hidden sm:table-cell">
                <button onClick={() => onSort('following')} className="group flex items-center gap-2 font-semibold text-gray-900 hover:text-blue-600 transition-colors" aria-label={`Sort by following ${sortField === 'following' ? sortDirection === 'asc' ? 'descending' : 'ascending' : 'ascending'}`}>
                  Following
                  {getSortIcon('following')}
                </button>
              </th>
              <th className="text-left p-4 hidden md:table-cell">
                <button onClick={() => onSort('posts')} className="group flex items-center gap-2 font-semibold text-gray-900 hover:text-blue-600 transition-colors" aria-label={`Sort by posts ${sortField === 'posts' ? sortDirection === 'asc' ? 'descending' : 'ascending' : 'ascending'}`}>
                  Posts
                  {getSortIcon('posts')}
                </button>
              </th>
              <th className="text-left p-4 hidden lg:table-cell">
                <button onClick={() => onSort('lastScraped')} className="group flex items-center gap-2 font-semibold text-gray-900 hover:text-blue-600 transition-colors" aria-label={`Sort by last scraped date ${sortField === 'lastScraped' ? sortDirection === 'asc' ? 'descending' : 'ascending' : 'ascending'}`}>
                  Last Scraped
                  {getSortIcon('lastScraped')}
                </button>
              </th>
              <th className="text-center p-4 w-20">
                <span className="font-semibold text-gray-900">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <AnimatePresence>
              {profiles.map((profile, index) => <motion.tr key={profile.id} initial={{
              opacity: 0,
              y: 20
            }} animate={{
              opacity: 1,
              y: 0
            }} exit={{
              opacity: 0,
              y: -20
            }} transition={{
              duration: 0.3,
              delay: index * 0.05
            }} className="border-b border-gray-100/50 hover:bg-gray-50/30 transition-colors">
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                        {profile.profileName.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-gray-900">@{profile.profileName}</span>
                          {profile.verified && <div className="w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                              <span className="text-white text-xs">✓</span>
                            </div>}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="font-semibold text-gray-900">{formatNumber(profile.followers)}</span>
                  </td>
                  <td className="p-4 hidden sm:table-cell">
                    <span className="text-gray-700">{formatNumber(profile.following)}</span>
                  </td>
                  <td className="p-4 hidden md:table-cell">
                    <span className="text-gray-700">{formatNumber(profile.posts)}</span>
                  </td>
                  <td className="p-4 hidden lg:table-cell">
                    <div className="flex items-center gap-2 text-gray-600">
                      <Calendar className="w-4 h-4" aria-hidden="true" />
                      <span>{formatDate(profile.lastScraped)}</span>
                    </div>
                  </td>
                  <td className="p-4 text-center">
                    <a href={profile.profileUrl} target="_blank" rel="noopener noreferrer" className="inline-flex items-center justify-center w-8 h-8 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200" aria-label={`Visit ${profile.profileName}'s Instagram profile`}>
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </td>
                </motion.tr>)}
            </AnimatePresence>
          </tbody>
        </table>
      </div>
    </div>;
};
export default ProfileDataTable;