import React from 'react';
import { Search, X, Filter } from 'lucide-react';
import { motion } from 'framer-motion';
interface FilterBarProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  minFollowers: number | undefined;
  onMinFollowersChange: (value: number | undefined) => void;
  maxFollowers: number | undefined;
  onMaxFollowersChange: (value: number | undefined) => void;
  onClearFilters: () => void;
  hasActiveFilters: boolean;
  mpid?: string;
}
const FilterBar: React.FC<FilterBarProps> = ({
  searchTerm,
  onSearchChange,
  minFollowers,
  onMinFollowersChange,
  maxFollowers,
  onMaxFollowersChange,
  onClearFilters,
  hasActiveFilters
}) => {
  return <motion.section initial={{
    opacity: 0,
    y: -20
  }} animate={{
    opacity: 1,
    y: 0
  }} transition={{
    duration: 0.5
  }} className="bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl p-6 mb-8 shadow-sm" aria-label="Filter controls for Instagram profiles" data-magicpath-id="0" data-magicpath-path="FilterBar.tsx">
      <div className="flex items-center gap-3 mb-6" data-magicpath-id="1" data-magicpath-path="FilterBar.tsx">
        <Filter className="w-5 h-5 text-gray-600" aria-hidden="true" data-magicpath-id="2" data-magicpath-path="FilterBar.tsx" />
        <h2 className="text-lg font-semibold text-gray-900" data-magicpath-id="3" data-magicpath-path="FilterBar.tsx">Filter Profiles</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end" data-magicpath-id="4" data-magicpath-path="FilterBar.tsx">
        {/* Search Input */}
        <div className="md:col-span-2" data-magicpath-id="5" data-magicpath-path="FilterBar.tsx">
          <label htmlFor="profile-search" className="block text-sm font-medium text-gray-700 mb-2" data-magicpath-id="6" data-magicpath-path="FilterBar.tsx">
            Profile Name
          </label>
          <div className="relative" data-magicpath-id="7" data-magicpath-path="FilterBar.tsx">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" aria-hidden="true" data-magicpath-id="8" data-magicpath-path="FilterBar.tsx" />
            <input id="profile-search" type="text" value={searchTerm} onChange={e => onSearchChange(e.target.value)} placeholder="Search by profile name..." className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 bg-white/50 backdrop-blur-sm text-gray-900 placeholder-gray-500" aria-describedby="search-help" data-magicpath-id="9" data-magicpath-path="FilterBar.tsx" />
          </div>
          <p id="search-help" className="sr-only" data-magicpath-id="10" data-magicpath-path="FilterBar.tsx">
            Enter a profile name to filter the results
          </p>
        </div>

        {/* Min Followers */}
        <div data-magicpath-id="11" data-magicpath-path="FilterBar.tsx">
          <label htmlFor="min-followers" className="block text-sm font-medium text-gray-700 mb-2" data-magicpath-id="12" data-magicpath-path="FilterBar.tsx">
            Min Followers
          </label>
          <input id="min-followers" type="number" value={minFollowers ?? ''} onChange={e => onMinFollowersChange(e.target.value ? Number(e.target.value) : undefined)} placeholder="0" min="0" className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 bg-white/50 backdrop-blur-sm text-gray-900 placeholder-gray-500" aria-describedby="min-followers-help" data-magicpath-id="13" data-magicpath-path="FilterBar.tsx" />
          <p id="min-followers-help" className="sr-only" data-magicpath-id="14" data-magicpath-path="FilterBar.tsx">
            Enter minimum follower count to filter profiles
          </p>
        </div>

        {/* Max Followers */}
        <div data-magicpath-id="15" data-magicpath-path="FilterBar.tsx">
          <label htmlFor="max-followers" className="block text-sm font-medium text-gray-700 mb-2" data-magicpath-id="16" data-magicpath-path="FilterBar.tsx">
            Max Followers
          </label>
          <input id="max-followers" type="number" value={maxFollowers ?? ''} onChange={e => onMaxFollowersChange(e.target.value ? Number(e.target.value) : undefined)} placeholder="∞" min="0" className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 bg-white/50 backdrop-blur-sm text-gray-900 placeholder-gray-500" aria-describedby="max-followers-help" data-magicpath-id="17" data-magicpath-path="FilterBar.tsx" />
          <p id="max-followers-help" className="sr-only" data-magicpath-id="18" data-magicpath-path="FilterBar.tsx">
            Enter maximum follower count to filter profiles
          </p>
        </div>
      </div>

      {/* Clear Filters Button */}
      {hasActiveFilters && <motion.div initial={{
      opacity: 0,
      scale: 0.95
    }} animate={{
      opacity: 1,
      scale: 1
    }} exit={{
      opacity: 0,
      scale: 0.95
    }} transition={{
      duration: 0.2
    }} className="mt-6 flex justify-end" data-magicpath-id="19" data-magicpath-path="FilterBar.tsx">
          <button onClick={onClearFilters} className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 bg-gray-100/50 hover:bg-gray-200/50 border border-gray-200 rounded-lg transition-all duration-200 backdrop-blur-sm" aria-label="Clear all active filters" data-magicpath-id="20" data-magicpath-path="FilterBar.tsx">
            <X className="w-4 h-4" aria-hidden="true" data-magicpath-id="21" data-magicpath-path="FilterBar.tsx" />
            <span data-magicpath-id="22" data-magicpath-path="FilterBar.tsx">Clear Filters</span>
          </button>
        </motion.div>}
    </motion.section>;
};
export default FilterBar;