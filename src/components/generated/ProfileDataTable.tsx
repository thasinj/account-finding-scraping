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
  mpid?: string;
}
export type SortField = 'profileName' | 'followers' | 'following' | 'posts' | 'lastScraped';
export type SortDirection = 'asc' | 'desc';
interface ProfileDataTableProps {
  profiles: InstagramProfile[];
  sortField: SortField | null;
  sortDirection: SortDirection;
  onSort: (field: SortField) => void;
  loading?: boolean;
  mpid?: string;
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
      return <ChevronUp className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" data-magicpath-id="0" data-magicpath-path="ProfileDataTable.tsx" />;
    }
    return sortDirection === 'asc' ? <ChevronUp className="w-4 h-4 text-blue-600" data-magicpath-id="1" data-magicpath-path="ProfileDataTable.tsx" /> : <ChevronDown className="w-4 h-4 text-blue-600" data-magicpath-id="2" data-magicpath-path="ProfileDataTable.tsx" />;
  };
  if (loading) {
    return <div className="bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl overflow-hidden shadow-sm" data-magicpath-id="3" data-magicpath-path="ProfileDataTable.tsx">
        <div className="p-8 text-center" data-magicpath-id="4" data-magicpath-path="ProfileDataTable.tsx">
          <div className="animate-spin w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full mx-auto mb-4" data-magicpath-id="5" data-magicpath-path="ProfileDataTable.tsx"></div>
          <p className="text-gray-600" data-magicpath-id="6" data-magicpath-path="ProfileDataTable.tsx">Loading profiles...</p>
        </div>
      </div>;
  }
  if (profiles.length === 0) {
    return <div className="bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl overflow-hidden shadow-sm" data-magicpath-id="7" data-magicpath-path="ProfileDataTable.tsx">
        <div className="p-12 text-center" data-magicpath-id="8" data-magicpath-path="ProfileDataTable.tsx">
          <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" data-magicpath-id="9" data-magicpath-path="ProfileDataTable.tsx" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2" data-magicpath-id="10" data-magicpath-path="ProfileDataTable.tsx">No profiles found</h3>
          <p className="text-gray-600" data-magicpath-id="11" data-magicpath-path="ProfileDataTable.tsx">Try adjusting your filters to see more results.</p>
        </div>
      </div>;
  }
  return <div className="bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl overflow-hidden shadow-sm" data-magicpath-id="12" data-magicpath-path="ProfileDataTable.tsx">
      <div className="overflow-x-auto" data-magicpath-id="13" data-magicpath-path="ProfileDataTable.tsx">
        <table className="w-full" role="table" aria-label="Instagram profiles data" data-magicpath-id="14" data-magicpath-path="ProfileDataTable.tsx">
          <thead data-magicpath-id="15" data-magicpath-path="ProfileDataTable.tsx">
            <tr className="border-b border-gray-200/50 bg-gray-50/50" data-magicpath-id="16" data-magicpath-path="ProfileDataTable.tsx">
              <th className="text-left p-4" data-magicpath-id="17" data-magicpath-path="ProfileDataTable.tsx">
                <button onClick={() => onSort('profileName')} className="group flex items-center gap-2 font-semibold text-gray-900 hover:text-blue-600 transition-colors" aria-label={`Sort by profile name ${sortField === 'profileName' ? sortDirection === 'asc' ? 'descending' : 'ascending' : 'ascending'}`} data-magicpath-id="18" data-magicpath-path="ProfileDataTable.tsx">
                  Profile Name
                  {getSortIcon('profileName')}
                </button>
              </th>
              <th className="text-left p-4" data-magicpath-id="19" data-magicpath-path="ProfileDataTable.tsx">
                <button onClick={() => onSort('followers')} className="group flex items-center gap-2 font-semibold text-gray-900 hover:text-blue-600 transition-colors" aria-label={`Sort by followers ${sortField === 'followers' ? sortDirection === 'asc' ? 'descending' : 'ascending' : 'ascending'}`} data-magicpath-id="20" data-magicpath-path="ProfileDataTable.tsx">
                  Followers
                  {getSortIcon('followers')}
                </button>
              </th>
              <th className="text-left p-4 hidden sm:table-cell" data-magicpath-id="21" data-magicpath-path="ProfileDataTable.tsx">
                <button onClick={() => onSort('following')} className="group flex items-center gap-2 font-semibold text-gray-900 hover:text-blue-600 transition-colors" aria-label={`Sort by following ${sortField === 'following' ? sortDirection === 'asc' ? 'descending' : 'ascending' : 'ascending'}`} data-magicpath-id="22" data-magicpath-path="ProfileDataTable.tsx">
                  Following
                  {getSortIcon('following')}
                </button>
              </th>
              <th className="text-left p-4 hidden md:table-cell" data-magicpath-id="23" data-magicpath-path="ProfileDataTable.tsx">
                <button onClick={() => onSort('posts')} className="group flex items-center gap-2 font-semibold text-gray-900 hover:text-blue-600 transition-colors" aria-label={`Sort by posts ${sortField === 'posts' ? sortDirection === 'asc' ? 'descending' : 'ascending' : 'ascending'}`} data-magicpath-id="24" data-magicpath-path="ProfileDataTable.tsx">
                  Posts
                  {getSortIcon('posts')}
                </button>
              </th>
              <th className="text-left p-4 hidden lg:table-cell" data-magicpath-id="25" data-magicpath-path="ProfileDataTable.tsx">
                <button onClick={() => onSort('lastScraped')} className="group flex items-center gap-2 font-semibold text-gray-900 hover:text-blue-600 transition-colors" aria-label={`Sort by last scraped date ${sortField === 'lastScraped' ? sortDirection === 'asc' ? 'descending' : 'ascending' : 'ascending'}`} data-magicpath-id="26" data-magicpath-path="ProfileDataTable.tsx">
                  Last Scraped
                  {getSortIcon('lastScraped')}
                </button>
              </th>
              <th className="text-center p-4 w-20" data-magicpath-id="27" data-magicpath-path="ProfileDataTable.tsx">
                <span className="font-semibold text-gray-900" data-magicpath-id="28" data-magicpath-path="ProfileDataTable.tsx">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody data-magicpath-id="29" data-magicpath-path="ProfileDataTable.tsx">
            <AnimatePresence data-magicpath-id="30" data-magicpath-path="ProfileDataTable.tsx">
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
            }} className="border-b border-gray-100/50 hover:bg-gray-50/30 transition-colors" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-id="31" data-magicpath-path="ProfileDataTable.tsx">
                  <td className="p-4" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-id="32" data-magicpath-path="ProfileDataTable.tsx">
                    <div className="flex items-center gap-3" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-id="33" data-magicpath-path="ProfileDataTable.tsx">
                      <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-semibold text-sm" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-id="34" data-magicpath-path="ProfileDataTable.tsx">
                        {profile.profileName.charAt(0).toUpperCase()}
                      </div>
                      <div data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-id="35" data-magicpath-path="ProfileDataTable.tsx">
                        <div className="flex items-center gap-2" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-id="36" data-magicpath-path="ProfileDataTable.tsx">
                          <span className="font-medium text-gray-900" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-field="profileName:unknown" data-magicpath-id="37" data-magicpath-path="ProfileDataTable.tsx">@{profile.profileName}</span>
                          {profile.verified && <div className="w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-id="38" data-magicpath-path="ProfileDataTable.tsx">
                              <span className="text-white text-xs" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-id="39" data-magicpath-path="ProfileDataTable.tsx">✓</span>
                            </div>}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="p-4" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-id="40" data-magicpath-path="ProfileDataTable.tsx">
                    <span className="font-semibold text-gray-900" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-field="followers:unknown" data-magicpath-id="41" data-magicpath-path="ProfileDataTable.tsx">{formatNumber(profile.followers)}</span>
                  </td>
                  <td className="p-4 hidden sm:table-cell" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-id="42" data-magicpath-path="ProfileDataTable.tsx">
                    <span className="text-gray-700" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-field="following:unknown" data-magicpath-id="43" data-magicpath-path="ProfileDataTable.tsx">{formatNumber(profile.following)}</span>
                  </td>
                  <td className="p-4 hidden md:table-cell" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-id="44" data-magicpath-path="ProfileDataTable.tsx">
                    <span className="text-gray-700" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-field="posts:unknown" data-magicpath-id="45" data-magicpath-path="ProfileDataTable.tsx">{formatNumber(profile.posts)}</span>
                  </td>
                  <td className="p-4 hidden lg:table-cell" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-id="46" data-magicpath-path="ProfileDataTable.tsx">
                    <div className="flex items-center gap-2 text-gray-600" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-id="47" data-magicpath-path="ProfileDataTable.tsx">
                      <Calendar className="w-4 h-4" aria-hidden="true" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-id="48" data-magicpath-path="ProfileDataTable.tsx" />
                      <span data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-field="lastScraped:unknown" data-magicpath-id="49" data-magicpath-path="ProfileDataTable.tsx">{formatDate(profile.lastScraped)}</span>
                    </div>
                  </td>
                  <td className="p-4 text-center" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-id="50" data-magicpath-path="ProfileDataTable.tsx">
                    <a href={profile.profileUrl} target="_blank" rel="noopener noreferrer" className="inline-flex items-center justify-center w-8 h-8 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200" aria-label={`Visit ${profile.profileName}'s Instagram profile`}>
                      <ExternalLink className="w-4 h-4" data-magicpath-uuid={(profile as any)["mpid"] ?? "unsafe"} data-magicpath-id="51" data-magicpath-path="ProfileDataTable.tsx" />
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