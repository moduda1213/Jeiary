import React from 'react';

interface InputFieldProps {
    label: string;
    type: string;
    placeholder?: string;
    id: string;
    value: string;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    icon?: boolean;
    onIconClick?: () => void;
}

export const InputField: React.FC<InputFieldProps> = ({ 
    label, type, placeholder, id, value, onChange, icon = false, onIconClick 
}) => (
    <div className="flex flex-col">
        <label htmlFor={id} className="mb-2 text-base font-medium text-[#1E1E1E] dark:text-gray-300">
            {label}
        </label>
        <div className="relative flex w-full items-stretch">
            <input
                id={id}
                type={type}
                value={value}
                onChange={onChange}
                placeholder={placeholder}
                className="form-input h-12 w-full flex-1 rounded-lg border border-[#E0E0E0] bg-white p-3 text-base text-[#1E1E1E] placeholder:text-[#6B7280] focus:border-primary focus:outline-none 
      focus:ring-2 focus:ring-primary/20 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400 dark:focus:border-primary"
            />
            {icon && (
                <button 
                    type="button" 
                    onClick={onIconClick}
                    className="absolute inset-y-0 right-0 flex items-center pr-3 text-[#6B7280] hover:text-[#1E1E1E] dark:text-gray-400 dark:hover:text-white"
                >
                    <span className="material-symbols-outlined">
                        {type === 'password' ? 'visibility' : 'visibility_off'}
                    </span>
                </button>
            )}
        </div>
    </div>
);