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
  }} className="bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl p-6 mb-8 shadow-sm" aria-label="Filter controls for Instagram profiles">
      <div className="flex items-center gap-3 mb-6">
        <Filter className="w-5 h-5 text-gray-600" aria-hidden="true" />
        <h2 className="text-lg font-semibold text-gray-900">Filter Profiles</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
        {/* Search Input */}
        <div className="md:col-span-2">
          <label htmlFor="profile-search" className="block text-sm font-medium text-gray-700 mb-2">
            Profile Name
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" aria-hidden="true" />
            <input id="profile-search" type="text" value={searchTerm} onChange={e => onSearchChange(e.target.value)} placeholder="Search by profile name..." className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 bg-white/50 backdrop-blur-sm text-gray-900 placeholder-gray-500" aria-describedby="search-help" />
          </div>
          <p id="search-help" className="sr-only">
            Enter a profile name to filter the results
          </p>
        </div>

        {/* Min Followers */}
        <div>
          <label htmlFor="min-followers" className="block text-sm font-medium text-gray-700 mb-2">
            Min Followers
          </label>
          <input id="min-followers" type="number" value={minFollowers ?? ''} onChange={e => onMinFollowersChange(e.target.value ? Number(e.target.value) : undefined)} placeholder="0" min="0" className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 bg-white/50 backdrop-blur-sm text-gray-900 placeholder-gray-500" aria-describedby="min-followers-help" />
          <p id="min-followers-help" className="sr-only">
            Enter minimum follower count to filter profiles
          </p>
        </div>

        {/* Max Followers */}
        <div>
          <label htmlFor="max-followers" className="block text-sm font-medium text-gray-700 mb-2">
            Max Followers
          </label>
          <input id="max-followers" type="number" value={maxFollowers ?? ''} onChange={e => onMaxFollowersChange(e.target.value ? Number(e.target.value) : undefined)} placeholder="∞" min="0" className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 bg-white/50 backdrop-blur-sm text-gray-900 placeholder-gray-500" aria-describedby="max-followers-help" />
          <p id="max-followers-help" className="sr-only">
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
    }} className="mt-6 flex justify-end">
          <button onClick={onClearFilters} className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 bg-gray-100/50 hover:bg-gray-200/50 border border-gray-200 rounded-lg transition-all duration-200 backdrop-blur-sm" aria-label="Clear all active filters">
            <X className="w-4 h-4" aria-hidden="true" />
            <span>Clear Filters</span>
          </button>
        </motion.div>}
    </motion.section>;
};
export default FilterBar;