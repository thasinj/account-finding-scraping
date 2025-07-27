import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import FilterBar from './FilterBar';
import ProfileDataTable from './ProfileDataTable';
import PaginationControls from './PaginationControls';
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

// Mock data for demonstration
const mockProfiles: InstagramProfile[] = [{
  id: '1',
  profileName: 'cristiano',
  followers: 615000000,
  following: 560,
  posts: 3420,
  lastScraped: '2024-01-15T10:30:00Z',
  verified: true,
  profileUrl: 'https://instagram.com/cristiano'
}, {
  id: '2',
  profileName: 'kyliejenner',
  followers: 400000000,
  following: 120,
  posts: 7200,
  lastScraped: '2024-01-15T09:15:00Z',
  verified: true,
  profileUrl: 'https://instagram.com/kyliejenner'
}, {
  id: '3',
  profileName: 'selenagomez',
  followers: 430000000,
  following: 300,
  posts: 1850,
  lastScraped: '2024-01-15T11:45:00Z',
  verified: true,
  profileUrl: 'https://instagram.com/selenagomez'
}, {
  id: '4',
  profileName: 'therock',
  followers: 395000000,
  following: 650,
  posts: 7800,
  lastScraped: '2024-01-15T08:20:00Z',
  verified: true,
  profileUrl: 'https://instagram.com/therock'
}, {
  id: '5',
  profileName: 'arianagrande',
  followers: 380000000,
  following: 800,
  posts: 4900,
  lastScraped: '2024-01-15T12:10:00Z',
  verified: true,
  profileUrl: 'https://instagram.com/arianagrande'
}];
export type SortField = 'profileName' | 'followers' | 'following' | 'posts' | 'lastScraped';
export type SortDirection = 'asc' | 'desc';
const InstagramProfilesTable: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [minFollowers, setMinFollowers] = useState<number | undefined>();
  const [maxFollowers, setMaxFollowers] = useState<number | undefined>();
  const [sortField, setSortField] = useState<SortField>('followers');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const filteredAndSortedProfiles = useMemo(() => {
    let filtered = mockProfiles.filter(profile => {
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
  }, [searchTerm, minFollowers, maxFollowers, sortField, sortDirection]);
  const paginatedProfiles = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filteredAndSortedProfiles.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredAndSortedProfiles, currentPage]);
  const totalPages = Math.ceil(filteredAndSortedProfiles.length / itemsPerPage);
  const handleClearFilters = () => {
    setSearchTerm('');
    setMinFollowers(undefined);
    setMaxFollowers(undefined);
    setSortField('followers');
    setSortDirection('desc');
    setCurrentPage(1);
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
  return <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 p-4 md:p-8">
      <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} transition={{
      duration: 0.6
    }} className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-2">
            Instagram Profiles
          </h1>
          <p className="text-lg text-gray-600">
            Scraped profile data with advanced filtering and sorting
          </p>
        </header>

        <FilterBar searchTerm={searchTerm} onSearchChange={setSearchTerm} minFollowers={minFollowers} onMinFollowersChange={setMinFollowers} maxFollowers={maxFollowers} onMaxFollowersChange={setMaxFollowers} onClearFilters={handleClearFilters} hasActiveFilters={hasActiveFilters} />

        <ProfileDataTable profiles={paginatedProfiles} sortField={sortField} sortDirection={sortDirection} onSort={handleSort} />

        <PaginationControls currentPage={currentPage} totalPages={totalPages} onPageChange={setCurrentPage} totalItems={filteredAndSortedProfiles.length} itemsPerPage={itemsPerPage} onItemsPerPageChange={setItemsPerPage} />
      </motion.div>
    </div>;
};
export default InstagramProfilesTable;