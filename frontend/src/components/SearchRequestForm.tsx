import { type FormEvent } from 'react';
import { useFormValidation } from '../hooks/useFormValidation';

interface SearchRequestFormProps {
  onSubmit: (data: SearchRequestData) => void;
  onCancel?: () => void;
  initialData?: SearchRequestData;
}

interface SearchRequestData {
  product_name: string;
  product_description: string;
  budget: number;
  platforms: string[];
  location?: string;
  match_threshold?: number;
  email_address?: string;
}

export default function SearchRequestForm({ 
  onSubmit, 
  onCancel,
  initialData 
}: SearchRequestFormProps) {
  const {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    validate,
    reset,
  } = useFormValidation(
    {
      productName: initialData?.product_name || '',
      productDescription: initialData?.product_description || '',
      budget: initialData?.budget?.toString() || '',
      platforms: initialData?.platforms || ([] as string[]),
      location: initialData?.location || '',
      matchThreshold: initialData?.match_threshold?.toString() || '70',
      emailAddress: initialData?.email_address || '',
    },
    {
      productName: (value) => {
        if (!value.trim()) return 'Product name is required';
        if (value.trim().length < 3) return 'Product name must be at least 3 characters';
        return null;
      },
      productDescription: (value) => {
        if (!value.trim()) return 'Product description is required';
        if (value.trim().length < 10) return 'Description must be at least 10 characters';
        return null;
      },
      budget: (value) => {
        if (!value) return 'Budget is required';
        if (isNaN(parseFloat(value))) return 'Invalid budget amount';
        if (parseFloat(value) <= 0) return 'Budget must be greater than 0';
        return null;
      },
      platforms: (_value) => {
        // No validation needed - empty platforms array means "search all platforms"
        return null;
      },
      matchThreshold: (value) => {
        if (value && isNaN(parseFloat(value))) return 'Invalid threshold';
        const threshold = parseFloat(value);
        if (value && (threshold < 0 || threshold > 100)) {
          return 'Threshold must be between 0 and 100';
        }
        return null;
      },
      emailAddress: (value) => {
        if (!value) return null; // Email is optional
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) return 'Invalid email address';
        return null;
      },
    }
  );

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!validate()) return;

    try {
      const formData: SearchRequestData = {
        product_name: values.productName.trim(),
        product_description: values.productDescription.trim(),
        budget: parseFloat(values.budget),
        platforms: values.platforms,
        location: values.location.trim() || undefined,
        match_threshold: values.matchThreshold ? parseFloat(values.matchThreshold) : 70,
        email_address: values.emailAddress.trim() || undefined,
      };

      await onSubmit(formData);
      reset();
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 animate-fade-in">
      <h2 className="text-2xl font-bold mb-6">Create Search Request</h2>
      
      {/* Product Name Input */}
      <div className="mb-4">
        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="productName">
          Product Name *
        </label>
        <input
          id="productName"
          type="text"
          value={values.productName}
          onChange={(e) => handleChange('productName', e.target.value)}
          onBlur={() => handleBlur('productName')}
          className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
            touched.productName && errors.productName ? 'border-red-500' : ''
          }`}
          placeholder="e.g., iPhone 13 Pro"
        />
        {touched.productName && errors.productName && (
          <p className="text-red-500 text-xs italic mt-1">{errors.productName}</p>
        )}
      </div>

      {/* Product Description Input */}
      <div className="mb-4">
        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="productDescription">
          Product Description *
        </label>
        <textarea
          id="productDescription"
          value={values.productDescription}
          onChange={(e) => handleChange('productDescription', e.target.value)}
          onBlur={() => handleBlur('productDescription')}
          rows={4}
          className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
            touched.productDescription && errors.productDescription ? 'border-red-500' : ''
          }`}
          placeholder="Describe the product you're looking for in detail..."
        />
        {touched.productDescription && errors.productDescription && (
          <p className="text-red-500 text-xs italic mt-1">{errors.productDescription}</p>
        )}
      </div>

      {/* Platform Checkboxes */}
      <div className="mb-4">
        <label className="block text-gray-700 text-sm font-bold mb-2">
          Platforms
        </label>
        <p className="text-gray-600 text-xs mb-2">Select specific platforms or leave empty to search all</p>
        <div className="flex flex-col space-y-2">
          {['craigslist', 'facebook', 'ebay'].map((platform) => (
            <label key={platform} className="inline-flex items-center">
              <input
                type="checkbox"
                checked={values.platforms.includes(platform)}
                onChange={(e) => {
                  const newPlatforms = e.target.checked
                    ? [...values.platforms, platform]
                    : values.platforms.filter(p => p !== platform);
                  handleChange('platforms', newPlatforms);
                }}
                onBlur={() => handleBlur('platforms')}
                className="form-checkbox h-5 w-5 text-blue-600"
              />
              <span className="ml-2 text-gray-700 capitalize">{platform}</span>
            </label>
          ))}
        </div>
        {touched.platforms && errors.platforms && (
          <p className="text-red-500 text-xs italic mt-1">{errors.platforms}</p>
        )}
      </div>

      {/* Budget Input */}
      <div className="mb-4">
        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="budget">
          Budget ($) *
        </label>
        <input
          id="budget"
          type="number"
          value={values.budget}
          onChange={(e) => handleChange('budget', e.target.value)}
          onBlur={() => handleBlur('budget')}
          className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
            touched.budget && errors.budget ? 'border-red-500' : ''
          }`}
          placeholder="1000"
          min="0"
          step="0.01"
        />
        {touched.budget && errors.budget && (
          <p className="text-red-500 text-xs italic mt-1">{errors.budget}</p>
        )}
        <p className="text-gray-600 text-xs mt-1">Maximum amount you're willing to pay</p>
      </div>

      {/* Location Input */}
      <div className="mb-4">
        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="location">
          Location
        </label>
        <input
          id="location"
          type="text"
          value={values.location}
          onChange={(e) => handleChange('location', e.target.value)}
          onBlur={() => handleBlur('location')}
          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          placeholder="e.g., San Francisco, CA"
        />
      </div>

      {/* Email Address Input */}
      <div className="mb-4">
        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="emailAddress">
          Email Address (Optional)
        </label>
        <input
          id="emailAddress"
          type="email"
          value={values.emailAddress}
          onChange={(e) => handleChange('emailAddress', e.target.value)}
          onBlur={() => handleBlur('emailAddress')}
          className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
            touched.emailAddress && errors.emailAddress ? 'border-red-500' : ''
          }`}
          placeholder="your@email.com"
        />
        {touched.emailAddress && errors.emailAddress && (
          <p className="text-red-500 text-xs italic mt-1">{errors.emailAddress}</p>
        )}
        <p className="text-gray-600 text-xs mt-1">
          Receive notifications for this search. Uses your global email preferences if set.
        </p>
      </div>

      {/* Match Threshold Input */}
      <div className="mb-6">
        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="matchThreshold">
          Match Threshold (%)
        </label>
        <input
          id="matchThreshold"
          type="number"
          value={values.matchThreshold}
          onChange={(e) => handleChange('matchThreshold', e.target.value)}
          onBlur={() => handleBlur('matchThreshold')}
          className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
            touched.matchThreshold && errors.matchThreshold ? 'border-red-500' : ''
          }`}
          placeholder="70"
          min="0"
          max="100"
        />
        {touched.matchThreshold && errors.matchThreshold && (
          <p className="text-red-500 text-xs italic mt-1">{errors.matchThreshold}</p>
        )}
        <p className="text-gray-600 text-xs mt-1">Minimum similarity score (0-100) for matches. Default: 70</p>
      </div>

      {/* Form Buttons */}
      <div className="flex items-center justify-between">
        <button
          type="submit"
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
          {initialData ? 'Update Search' : 'Create Search'}
        </button>
        
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

// Made with Bob
