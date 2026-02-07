import { Plus, Minus } from 'lucide-react';
import { useLocalSchedule } from '../../hooks/useLocalSchedule';

interface AddButtonProps {
  courseId: string;
}

export function AddButton({ courseId }: AddButtonProps) {
  const { addCourse, removeCourse, isInSchedule } = useLocalSchedule();
  const inSchedule = isInSchedule(courseId);

  const handleClick = async (e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (inSchedule) {
      await removeCourse(courseId);
    } else {
      await addCourse(courseId);
    }
  };

  return (
    <button
      onClick={handleClick}
      className={inSchedule ? "p-1.5 text-red-500" : "p-1.5 text-green-500"}
      title={inSchedule ? "Remove from schedule" : "Add to schedule"}
    >
      {inSchedule ? (
        <Minus className="w-5 h-5" />
      ) : (
        <Plus className="w-5 h-5" />
      )}
    </button>
  );
}
