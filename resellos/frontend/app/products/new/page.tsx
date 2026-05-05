'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { createProduct } from '@/lib/api';

const CATEGORIES = [
  'Electronics',
  'Home & Garden',
  'Toys & Games',
  'Sports',
  'Books',
  'Clothing',
  'Beauty',
  'Automotive',
  'Office Supplies',
  'Pet Supplies',
  'Jewelry',
  'Other',
];

const SUBCATEGORIES: Record<string, string[]> = {
  Electronics: ['Audio', 'Computer Accessories', 'Phone Accessories', 'Lighting', 'Cameras', 'Gaming'],
  'Home & Garden': ['Planters', 'Textiles', 'Kitchen', 'Bathroom', 'Outdoor', 'Decor'],
  'Toys & Games': ['Board Games', 'Action Figures', 'Educational', 'Puzzles', 'Outdoor Toys'],
  Sports: ['Fitness Equipment', 'Drinkware', 'Apparel', 'Outdoor Sports', 'Team Sports'],
  Books: ['Fiction', 'Non-Fiction', 'Textbooks', 'Children', 'Comics'],
  Clothing: ['Men', 'Women', 'Kids', 'Shoes', 'Accessories'],
  Beauty: ['Skincare', 'Makeup', 'Hair Care', 'Fragrances', 'Tools'],
  Automotive: ['Accessories', 'Electronics', 'Cleaning', 'Tools'],
  'Office Supplies': ['Stationery', 'Organization', 'Technology', 'Furniture'],
  'Pet Supplies': ['Dogs', 'Cats', 'Birds', 'Fish', 'Small Animals'],
  Jewelry: ['Necklaces', 'Rings', 'Bracelets', 'Earrings', 'Watches'],
  Other: ['General'],
};

export default function NewProductPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    subcategory: '',
    description: '',
    supplier_url: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const subcategories = formData.category
    ? SUBCATEGORIES[formData.category] || []
    : [];

  function validate() {
    const errs: Record<string, string> = {};
    if (!formData.name.trim()) errs.name = 'Product name is required';
    if (!formData.category) errs.category = 'Category is required';
    return errs;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length > 0) {
      setErrors(errs);
      return;
    }

    setLoading(true);
    try {
      const product = await createProduct({
        name: formData.name.trim(),
        category: formData.category,
        subcategory: formData.subcategory || undefined,
        description: formData.description.trim() || undefined,
        supplier_url: formData.supplier_url.trim() || undefined,
      });

      if (product) {
        router.push(`/products/${product.id}`);
      } else {
        setErrors({ form: 'Failed to create product. Please try again.' });
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 max-w-2xl">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link
          href="/products"
          className="p-2 rounded-lg text-[#71717a] hover:text-white hover:bg-[#1a1a1a] transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-semibold text-white">New Product</h1>
          <p className="text-sm text-[#71717a] mt-0.5">
            Add a new product to research
          </p>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-5">
        {errors.form && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            {errors.form}
          </div>
        )}

        {/* Product Name */}
        <div>
          <label className="block text-sm font-medium text-white mb-1.5">
            Product Name <span className="text-red-400">*</span>
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => {
              setFormData((f) => ({ ...f, name: e.target.value }));
              if (errors.name) setErrors((er) => ({ ...er, name: '' }));
            }}
            placeholder="e.g., Portable Bluetooth Speaker"
            className={`w-full px-3 py-2.5 bg-[#1a1a1a] border rounded-lg text-sm text-white placeholder:text-[#71717a] focus:outline-none focus:ring-1 ${
              errors.name
                ? 'border-red-500/50 focus:border-red-500/50'
                : 'border-[#27272a] focus:border-indigo-500/50 focus:ring-indigo-500/20'
            }`}
          />
          {errors.name && (
            <p className="mt-1 text-xs text-red-400">{errors.name}</p>
          )}
        </div>

        {/* Category */}
        <div>
          <label className="block text-sm font-medium text-white mb-1.5">
            Category <span className="text-red-400">*</span>
          </label>
          <select
            value={formData.category}
            onChange={(e) => {
              setFormData((f) => ({
                ...f,
                category: e.target.value,
                subcategory: '',
              }));
              if (errors.category) setErrors((er) => ({ ...er, category: '' }));
            }}
            className={`w-full px-3 py-2.5 bg-[#1a1a1a] border rounded-lg text-sm text-white focus:outline-none focus:ring-1 ${
              errors.category
                ? 'border-red-500/50 focus:border-red-500/50'
                : 'border-[#27272a] focus:border-indigo-500/50 focus:ring-indigo-500/20'
            }`}
          >
            <option value="">Select a category</option>
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
          {errors.category && (
            <p className="mt-1 text-xs text-red-400">{errors.category}</p>
          )}
        </div>

        {/* Subcategory */}
        {subcategories.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-white mb-1.5">
              Subcategory
            </label>
            <select
              value={formData.subcategory}
              onChange={(e) =>
                setFormData((f) => ({ ...f, subcategory: e.target.value }))
              }
              className="w-full px-3 py-2.5 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-white focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20"
            >
              <option value="">Select a subcategory (optional)</option>
              {subcategories.map((sub) => (
                <option key={sub} value={sub}>
                  {sub}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-white mb-1.5">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) =>
              setFormData((f) => ({ ...f, description: e.target.value }))
            }
            placeholder="Optional product description, notes, or research observations..."
            rows={4}
            className="w-full px-3 py-2.5 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-white placeholder:text-[#71717a] focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 resize-none"
          />
        </div>

        {/* Supplier URL */}
        <div>
          <label className="block text-sm font-medium text-white mb-1.5">
            Supplier URL
          </label>
          <input
            type="url"
            value={formData.supplier_url}
            onChange={(e) =>
              setFormData((f) => ({ ...f, supplier_url: e.target.value }))
            }
            placeholder="https://www.alibaba.com/product/..."
            className="w-full px-3 py-2.5 bg-[#1a1a1a] border border-[#27272a] rounded-lg text-sm text-white placeholder:text-[#71717a] focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20"
          />
          <p className="mt-1 text-xs text-[#71717a]">
            Optional. Link to the supplier product page for auto-research.
          </p>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3 pt-2">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/50 text-white text-sm font-medium rounded-lg transition-colors"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Creating...
              </>
            ) : (
              'Create Product'
            )}
          </button>
          <Link
            href="/products"
            className="px-5 py-2.5 text-sm text-[#a1a1aa] hover:text-white transition-colors"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
