package disi.savinglives_backend.services;

import disi.savinglives_backend.entities.InformativeContent;
import disi.savinglives_backend.repositories.InformativeContentRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class InformativeContentService {

    private final InformativeContentRepository informativeContentRepository;

    public List<InformativeContent> get(){
        List<InformativeContent> list = informativeContentRepository.findAll();
        return list;
    }

    public boolean delete(UUID id) {
        Optional<InformativeContent> content = informativeContentRepository.findById(id);
        if (content.isPresent()) {
            informativeContentRepository.deleteById(id);
            return true;
        } else {
            return false;
        }
    }

    public InformativeContent create(InformativeContent informativeContent) {
        return informativeContentRepository.save(informativeContent);
    }


}
